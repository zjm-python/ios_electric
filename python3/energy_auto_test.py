import subprocess
import sys
import getopt
import time
import os
import parse_battery_info
import usb_ctrl_client

"""
  Author: mjzheng
  Date: 20201-01-11
"""


def get_cmd_parameter(argv):
    uuid = ''
    output_dir = ''
    bundle_id = ''
    app_name = ''
    try:
        options, _ = getopt.getopt(argv, "hu:o:b:n:", ["uuid=", "output_dir=", "bundle_id=", "name="])
    except getopt.GetoptError:
        print('usage : energy_auto_test.py -u <uuid> -o <output_dir> -b <bundle_id> -n <name>')
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            print('usage : energy_auto_test.py -u <uuid> -o <output_dir> -b <bundle_id> -n <name>')
            sys.exit()
        elif opt in ("-u", "--uuid"):
            uuid = arg
        elif opt in ("-o", "--output_dir"):
            output_dir = arg
        elif opt in ("-b", "--bundle_id"):
            bundle_id = arg
        elif opt in ("-n", "--name"):
            app_name = arg

    print('get param:', uuid, output_dir, bundle_id)
    if len(uuid) == 0 or len(output_dir) == 0 or len(bundle_id) == 0:
        print('usage : energy_auto_test.py -u <uuid> -o <output_dir> -b <bundle_id> -n <name>')
        sys.exit()
    return uuid, output_dir, bundle_id, app_name


def get_latest_file(input_dir) :
    g = os.walk(input_dir)
    last_ts = 0
    last_path = ''
    for path, _, file_list in g:
        for file_name in file_list:
            if file_name.endswith(".PLSQL"):
                file_path = os.path.join(path, file_name)
                t = os.path.getctime(file_path)
                if t > last_ts:
                    last_ts = t
                    last_path = file_path
    return last_path


def sync_device(uuid, output_dir):
    print('start sync device')
    sync_cmd = r'idevicecrashreport'  # 这里r可以可以不管空格和中文字符的烦恼
    child = subprocess.Popen(sync_cmd + ' -u ' + uuid + ' ' + output_dir, shell=True)
    return_code = child.wait()
    print('sync result ', return_code)


def parse_energy(output_dir, bundle_id, app_name):
    print('start parse energy')
    input_file = get_latest_file(output_dir)
    print('get best input file ', input_file)
    print('start parse energy file', input_file)
    parse_battery_info.parse_battery_info(input_file, bundle_id, app_name, output_dir)


def get_battery_info(uuid):
    sync_cmd = r'ideviceinfo'  # 这里r可以可以不管空格和中文字符的烦恼
    child = subprocess.Popen(sync_cmd + ' -u ' + uuid +
                             ' --domain com.apple.mobile.battery', shell=True, stdout=subprocess.PIPE)
    stdout, _    = child.communicate()
    print(stdout)
    lines = stdout.splitlines()
    battery_level = 0
    is_full_charged = False
    for row in lines:
        line = row.decode()
        first, second = line.split(':')
        if first == 'BatteryCurrentCapacity':
            print(first, second)
            battery_level = int(second)
            continue
        if first == 'FullyCharged':
            print(first, second)
            second = second.strip()
            if second == 'true':
                is_full_charged = True
            continue

    print('get battery level', battery_level, is_full_charged)
    return battery_level, is_full_charged


def wait_full_charged(uuid):
    while True:
        level, is_full = get_battery_info(uuid)
        if is_full or level >= 98:
            break
        time.sleep(5)
    return True


def format_timestamp(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def wait_next_integral_hour():
    one_hour = 3600
    cur_time = int(time.time())
    current_hour = cur_time - (cur_time % one_hour)
    next_hour = current_hour + one_hour
    diff_seconds = next_hour - cur_time

    print('current hour', format_timestamp(current_hour), 'next hour',
          format_timestamp(next_hour), 'diff_seconds', diff_seconds)
    time.sleep(diff_seconds)
    return cur_time


def wait_sync_device(start_time):
    one_hour = 3600
    start_hour = start_time - (start_time % one_hour)

    # 数据延迟1小时输出，再多等10分钟
    end_time = start_hour + 2*one_hour + 600
    remain_seconds = 0
    cur_time = int(time.time())
    if end_time > cur_time:
        remain_seconds = end_time - cur_time
    print('sync device start time', format_timestamp(start_time), 'current time',
          format_timestamp(cur_time), 'end time', format_timestamp(end_time), 'remain seconds', remain_seconds)
    time.sleep(remain_seconds)


def do_real_test():
    print('implement this interface to do real test')
    #time.sleep(10)
    wait_next_integral_hour()
    print('finish test')


def energy_auto_test(ip, port, uuid, output_dir, bundle_id, app_name):
    # 连接数据线，充电
    print('step 1: start connect data line and charged')
    usb_ctrl_client.usb_ctrl_client(ip, port, 1)

    # 充满电
    wait_full_charged(uuid)
    print('step 2: in full charged state')

    # 测试前整点同步一次数据，注意同步时间为整点
    sync_device(uuid, output_dir)
    print('step 3: sync device before test')

    # 等待下一次整点
    wait_next_integral_hour()
    start_time = int(time.time())
    print('step 4: reach integral point', start_time)

    # 断开充电和连接的数据线
    usb_ctrl_client.usb_ctrl_client(ip, port, 0)
    print('step 5: disconnect data line')

    # 模拟测试, 结束测试时间为开始时间+3600s, 也对应整点
    do_real_test()
    print('step 6: finish app test')

    # 开始充电和连接数据线
    usb_ctrl_client.usb_ctrl_client(ip, port, 1)
    print('step 7: reconnect data line and charged')

    return start_time


def energy_auto_test_cycle(ip, port, uuid, output_dir, bundle_id, app_name, times):
    start_time = 0
    for i in range(times):
        print('test cycle', i)
        start_time = energy_auto_test(ip, port, uuid, output_dir, bundle_id, app_name)
    # 等待同步和解析
    wait_sync_parse(uuid, output_dir, bundle_id, app_name, start_time)


def sync_and_parse(uuid, output_dir, bundle_id, app_name):
    sync_device(uuid, output_dir)
    parse_energy(output_dir, bundle_id, app_name)


def wait_sync_parse(uuid, output_dir, bundle_id, app_name, start_time):
    wait_sync_device(start_time)
    sync_and_parse(uuid, output_dir, bundle_id, app_name)


if __name__ == "__main__":
    uuid, output_dir, bundle_id, app_name = get_cmd_parameter(sys.argv[1:])
    print('read param:', uuid, output_dir, bundle_id)
    sync_and_parse(uuid, output_dir, bundle_id, app_name)
