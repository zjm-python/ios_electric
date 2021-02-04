performace tools for mac

# 前置条件
```
sh setup.sh
```
# Mac用Homebrew安装libimobiledevice 指引
- https://developer.apple.com/download/more/?=for%20Xcode安装最新版的Command Line Tools。即使你装了最新版的Xcode，后续仍可能报错。
- sync cmd : idevicecrashreport -u [uuid] [dir]
- ideviceinfo -u <device udid> --domain com.apple.mobile.battery
- ideviceinfo -u 6daac09469e94a24a2fa1f684bcd57963fd29c25 --domain com.apple.mobile.battery


# some sample cmd
- sample : idevicecrashreport -u 6daac09469e94a24a2fa1f684bcd57963fd29c25 /Users/mjzheng/Downloads/mj_iphone/
- python energy_auto_test.py -u 6daac09469e94a24a2fa1f684bcd57963fd29c25 -o /Users/mjzheng/Downloads/mj_iphone/ -b com.tencent.meeting.db.haven -n meeting
- python -c "import read_ios_battery_info; read_ios_battery_info.read_ios_battery_info('/Users/mjzheng/Downloads/mj_iphone/powerlog_2021-01-14_14-58_C2968A4D.PLSQL', 'com.tencent.meeting.db.haven', '/Users/mjzheng/Downloads/mj_iphone/')"
- python -c "import usb_ctrl_client; usb_ctrl_client.usb_ctrl_client(1, '10.6.66.48', 9002)"
- python -c "import energy_auto_test; energy_auto_test.get_battery_info('6daac09469e94a24a2fa1f684bcd57963fd29c25')"
- python2 -c "import energy_auto_test; energy_auto_test.energy_auto_test_cycle('10.6.66.48', 9002, '6daac09469e94a24a2fa1f684bcd57963fd29c25', '/Users/mjzheng/Downloads/mj_iphone/', 'com.tencent.meeting.db.haven', '腾讯会议', 10)"
- python -c "import parse_battery_info; parse_battery_info.parse_battery_info('/Users/mjzheng/Downloads/mj_iphone/powerlog_2021-01-19_09-18_67D3742A.PLSQL', 'com.tencent.meeting.db.haven', '腾讯会议', '/Users/mjzheng/Downloads/mj_iphone/')"
- python usb_ctrl_server.py -i [ip] -p [port]
- python -m venv envname


python2 -c "import energy_auto_test; energy_auto_test.energy_auto_test_cycle('10.6.66.48', 9002, '8085c3088ef403c8715e8c01af2ab10e9adebe90', '/Users/mjzheng/Downloads/wp_iphone/', 'com.tencent.meeting', '腾讯会议', 1)"

python2 -c "import energy_auto_test; energy_auto_test.energy_auto_test_cycle('10.6.66.48', 9002, 'f1872d72173c71834ce03b68cfff0f3a985e3371', '/Users/mjzheng/Downloads/wp_iphone/', 'com.tencent.meeting', '腾讯会议', 1)"

python2 -c "import energy_auto_test; energy_auto_test.energy_auto_test_with_config()"

# 1. PowerMoitor
run `python PowerMoitor.py`

python energy_auto_test.py -u 658db9e5fe235c8a51746722e6186a1ad89b8cdd -o /Users/mjzheng/Downloads/wp_iphone/ -b com.tencent.meeting -n meeting

# 电量自动化使用说明
- 环境安装：在mac上运行setup.sh 
- windows 端连接usb控制电路板的充电线
- Mac 端连接usb控制电路板的其中一条数据线（）Type A 接口
- iphone 连接usb控制电路板的同条数据线的另外一段
- Windows 端开启usb 控制电路板服务程序，"python usb_ctrl_server.py -i [ip] -p [port]"
- 开始电路自动化测试, 参照例子：python -c "import energy_auto_test; energy_auto_test.energy_auto_test('10.6.66.48', 9002, '6daac09469e94a24a2fa1f684bcd57963fd29c25', '/Users/mjzheng/Downloads/mj_iphone/', 'com.tencent.meeting.db.haven', '腾讯会议')"