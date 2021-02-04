import sqlite3
import datetime
import time
from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.charts import Grid
import tkinter


def percent(expression):
    if "%" in expression:
        expression = expression.replace("%", "/100")
    result = eval(expression)
    #print(result)
    return result


def percent_add(a1, a2):
    v1 = percent(a1)
    v2 = percent(a2)
    return ratio(v1+v2)


def ratio(a):
    b = str(a*100) + '%'
    #print(b)
    return b


class RectDef:
    def __init__(self):
        self.top = ''
        self.left = ''
        self.bottom = ''
        self.right = ''


def format_timestamp(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def get_rect(cell_top, cell_left, cell_width, cell_height):
    pos = RectDef()
    pos.top = cell_top
    pos.left = cell_left
    pos.right = percent_add(pos.left, cell_width)
    pos.bottom = percent_add(pos.right, cell_height)
    return pos


def get_battery_level(cursor):
    cursor.execute("SELECT datetime(timestamp, 'unixepoch', 'localtime'), "
                   "Level from PLBatteryAgent_EventBackward_Battery")
    l = cursor.fetchall()
    lx = []
    ly = []
    for (x, y) in l:
        lx.append(x)
        ly.append(y)
    return lx, ly


def get_battery_capacity(cursor):
    cursor.execute("SELECT"
                   " datetime(timestamp, 'unixepoch', 'localtime'),"
                   " AbsoluteCapacity,"
                   " timestamp"
                   " from PLBatteryAgent_EventBackward_Battery"
                   #" where IsCharging=0"
                   " order by timestamp ")
    l = cursor.fetchall()
    count = len(l)
    if count == 0:
        return
    min_ts = l[0][2];

    one_hour = 3600
    current_hour = min_ts - (min_ts % one_hour)
    print('min timesamp', min_ts, current_hour)
    next_hour = current_hour + one_hour

    ls_hour = []
    for (x, y, z) in l:
        #print ('add ', x, y, z)
        if z >= next_hour:
            current_hour = next_hour
            next_hour = current_hour + one_hour
            #print(format_timestamp(current_hour), format_timestamp(next_hour), format_timestamp(z), '\n')
            ls_hour.append([x, y, z])
            print ('add ', x, y, z)

    ls_cap = []
    #print(len(ls_hour))
    ls_hour_count = len(ls_hour)
    for i in range(ls_hour_count-1):
        delta = ls_hour[i][1] - ls_hour[i+1][1]
        if delta >= 0:
            ts = ls_hour[i][0]
            ls_cap.append([ts, delta])

    lx = []
    ly = []
    for (x, y) in ls_cap:
        lx.append(x)
        ly.append(y)
    #print(type(l))
    return lx, ly


def get_app_energy(cursor, bundle_id):
    cursor.execute("SELECT"
                   " datetime(timestamp, 'unixepoch', 'localtime'),"
                   " timestamp,"
                   " sum(Energy) as hour_energy,"
                   " NodeID,"
                   " (select Name From PLAccountingOperator_EventNone_Nodes "
                   " where ID=PLAccountingOperator_Aggregate_RootNodeEnergy.NodeID) AS NodeName,"
                   " (select avg(Voltage) from PLBatteryAgent_EventBackward_Battery "
                   " where PLBatteryAgent_EventBackward_Battery.timestamp "
                   " between PLAccountingOperator_Aggregate_RootNodeEnergy.timestamp "
                   " and (PLAccountingOperator_Aggregate_RootNodeEnergy.timestamp+3600) ) as av_voltage,"
                   " (select ScreenOnTime from PLAppTimeService_Aggregate_AppRunTime "
                   " where BundleID='{}' and "
                   " PLAppTimeService_Aggregate_AppRunTime.timestamp="
                   "PLAccountingOperator_Aggregate_RootNodeEnergy.timestamp) as app_runtime"
                   " from PLAccountingOperator_Aggregate_RootNodeEnergy"
                   " where NodeID=(select ID from PLAccountingOperator_EventNone_Nodes where Name ='{}')"
                   " group by timestamp"
                   " order by timestamp ".format(bundle_id, bundle_id))

    l = cursor.fetchall()

    l_x = []
    l_y = []
    l_y1 = []

    l1_x = []
    l1_y = []
    l1_y1 = []
    #app_name = ''
    for (datetime, _, real_energy, _, _, voltage, app_time) in l:
        if type(app_time) == float and 10 <= app_time <= 3600 :
            l_x.append(datetime)
            l_y.append(real_energy)
            hour_energy = (real_energy / app_time) * 3600
            l_y1.append(hour_energy)
            if type(voltage) == float and voltage > 0:
                l1_x.append(datetime)
                l1_y.append(real_energy / voltage)
                l1_y1.append(hour_energy / voltage)
            print(datetime, hour_energy, real_energy, app_time, '\n')
    return l_x, l_y, l_y1, l1_x, l1_y, l1_y1


def get_pyecharts_line(lx, ly, lx_unit, ly_unit, l_tile, pos):
    line = Line()
    left = percent(pos.left)
    right = percent(pos.right)
    center_point = left + (right - left) / 2
    leg_left = ratio(center_point - 0.1)
    title_left = ratio(center_point)
    top = percent(pos.top)
    new_top = ratio(top - 0.05)

    line.add_xaxis(lx)
    line.add_yaxis(ly_unit, ly)
    line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line.set_global_opts(title_opts=opts.TitleOpts(title=l_tile, pos_top=new_top, pos_left=title_left),
                         yaxis_opts=opts.AxisOpts(name=ly_unit),
                         xaxis_opts=opts.AxisOpts(name=lx_unit),
                         legend_opts=opts.LegendOpts(pos_top=new_top, pos_left=leg_left),
                         )
    return line


def get_pyecharts_line2(lx, ly, ly1, lx_unit, ly_unit, ly1_unit, l_tile, pos):
    line = get_pyecharts_line(lx, ly, lx_unit, ly_unit, l_tile, pos)
    line.add_yaxis(ly1_unit, ly1)
    line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    return line


def get_app_detail(cursor, bundle_id):
    cursor.execute("SELECT ID FROM 'PLAccountingOperator_EventNone_Nodes' WHERE Name='{}'".format(bundle_id))
    myid = cursor.fetchall()[0][0]
    #print(myid)

    cursor.execute("SELECT ID, Name FROM 'PLAccountingOperator_EventNone_Nodes'")
    # print(cursor.fetchall())
    nodename = {}
    for (id, name) in cursor.fetchall():
        nodename[id] = name
    #print(nodename)

    cursor.execute("SELECT RootNodeID FROM 'PLAccountingOperator_Aggregate_RootNodeEnergy'  WHERE NodeID = {} \
                GROUP BY RootNodeID" \
                   .format(myid))
    l = cursor.fetchall()

    type_list = []
    for (t,) in l:
        type_list.append(t)
    # print(type_list)

    cursor.execute("SELECT datetime(timestamp, 'unixepoch', 'localtime') \
                FROM 'PLAccountingOperator_Aggregate_RootNodeEnergy'  WHERE NodeID = {} GROUP BY timestamp"
                   .format(myid))
    l = cursor.fetchall()

    time_list = []
    for (t,) in l:
        time_list.append(t)
    # print(time_list)

    m = {}
    m_c = {}
    m_h = {}
    for t in type_list:
        m[t] = {}
        m_c[t] = {}
        m_h[t] = {}
        for time in time_list:
            m[t][time] = ""
            m_c[t][time] = ""
            m_h[t][time] = ""
    # print(m)

    cursor.execute(
        "SELECT datetime(timestamp, 'unixepoch', 'localtime'),"
        " Energy, "
        " RootNodeID, "
        " (select avg(Voltage) from PLBatteryAgent_EventBackward_Battery "
        " where PLBatteryAgent_EventBackward_Battery.timestamp "
        " between PLAccountingOperator_Aggregate_RootNodeEnergy.timestamp "
        " and (PLAccountingOperator_Aggregate_RootNodeEnergy.timestamp+3600) ) as av_voltage,"
        " (select ScreenOnTime from PLAppTimeService_Aggregate_AppRunTime "
                   " where BundleID='{}' and "
                   " PLAppTimeService_Aggregate_AppRunTime.timestamp="
                   "PLAccountingOperator_Aggregate_RootNodeEnergy.timestamp) as app_runtime"
        " FROM 'PLAccountingOperator_Aggregate_RootNodeEnergy'  "
        " WHERE NodeID = '{}'".format(bundle_id, myid)
    )
    l = cursor.fetchall()
    # print(l)

    for (t, e, rootid, voltage, app_time) in l:
        print('get ', t, e, voltage, app_time, '\n')
        m[rootid][t] = float(e)
        if type(voltage) == float and voltage > 0:
            m_c[rootid][t] = float(e/voltage)
        if type(app_time) == float and 10 <= app_time <= 3600:
            m_h[rootid][t] = float((e / app_time) * 3600)

    # print(m)
    m2 = {}

    for t in type_list:
        m2[t] = list(m[t].values())

    m2_c = {}
    for t in type_list:
        m2_c[t] = list(m_c[t].values())

    m3_c = {}
    for t in type_list:
        m3_c[t] = list(m_h[t].values())
    #print(m2)
    return time_list, type_list, nodename, m2, m2_c, m3_c


def get_bar(time_list, type_list, node_name, m2, lx_unit, ly_unit, l_tile, pos):
    detail_bar = Bar()
    detail_bar.add_xaxis(time_list)
    detail_bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    for t in type_list:
        detail_bar.add_yaxis(node_name[t], m2[t])

    left = percent(pos.left)
    right = percent(pos.right)
    center_point = left + (right - left) / 2

    # leg_left = ratio(center_point - 0.05)
    title_left = ratio(center_point)
    top = percent(pos.top)
    new_top = ratio(top - 0.05)

    detail_bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    detail_bar.set_global_opts(title_opts=opts.TitleOpts(title=l_tile, pos_top=pos.top, pos_left=title_left),
                               yaxis_opts=opts.AxisOpts(name=ly_unit),
                               xaxis_opts=opts.AxisOpts(name=lx_unit),
                               legend_opts=opts.LegendOpts(pos_top=new_top, pos_left=pos.left),
                               )
    return detail_bar


def parse_battery_info(input_file, bundle_id, app_name, output_dir):
    con = sqlite3.connect(input_file)
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    cursor.fetchall()

    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    file_name = output_dir + current_time + '_battery_info.html'

    cell_width = '40%'
    cell_height = '20%'

    lx_level, ly_level = get_battery_level(cursor)
    level_pos = get_rect('5%', '5%', cell_width, cell_height)
    line_level = get_pyecharts_line(lx_level, ly_level, "", "(电量百分比)", "系统电量百分比", level_pos)

    lx_cap, ly_cap = get_battery_capacity(cursor)
    cap_pos = get_rect('5%', '55%', cell_width, cell_height)
    line_cap = get_pyecharts_line(lx_cap, ly_cap, "", "(每小时耗电)", "系统每小时耗电量", cap_pos)

    app_l_x, app_l_y, app_l_y1, app_l1_x, app_l1_y, app_l1_y1 = get_app_energy(cursor, bundle_id)
    app_mwh_pos = get_rect('35%', '5%', cell_width, cell_height)
    line_app_mwh = get_pyecharts_line2(app_l_x, app_l_y, app_l_y1, "",
                                       "(实际能耗)", "（每小时能耗）", app_name + "每小时能耗", app_mwh_pos)

    app_mah_pos = get_rect('35%', '55%', cell_width, cell_height)
    line_app_mah = get_pyecharts_line2(app_l1_x, app_l1_y, app_l1_y1, "",
                                       "(实际电量)", "(每小时电量)", app_name + "每小时耗电量", app_mah_pos)


    time_list, type_list, node_name, m2, m2_c, _ = get_app_detail(cursor, bundle_id)
    app_detail_pos = get_rect('65%', '5%', cell_width, cell_height)
    detail_bar = get_bar(time_list, type_list, node_name, m2, "", "(mWh)", app_name + "每小时能耗详情", app_detail_pos)
    app_detail_pos1 = get_rect('65%', '55%', cell_width, cell_height)
    detail_bar1 = get_bar(time_list, type_list, node_name, m2_c, "", "(mAh)", app_name + "每小时耗电量详情", app_detail_pos1)


    screen = tkinter.Tk()
    print(screen.winfo_screenheight(), screen.winfo_screenwidth())
    grid = Grid(
        init_opts=opts.InitOpts(
            # 设置宽度、高度
            width=str(screen.winfo_screenwidth()) + 'px',
            height=str(screen.winfo_screenheight()) + 'px',
        )
    )  # 初始化，参数可传page_title,width,height
    grid.add(line_level, grid_opts=opts.GridOpts(pos_top=level_pos.top,
                                                 pos_left=level_pos.left,
                                                 height=cell_height,
                                                 width=cell_width))
    grid.add(line_cap, grid_opts=opts.GridOpts(pos_top=cap_pos.top,
                                               pos_left=cap_pos.left,
                                               height=cell_height,
                                               width=cell_width))
    grid.add(line_app_mwh, grid_opts=opts.GridOpts(pos_top=app_mwh_pos.top,
                                                   pos_left=app_mwh_pos.left,
                                                   height=cell_height,
                                                   width=cell_width))
    grid.add(line_app_mah, grid_opts=opts.GridOpts(pos_top=app_mah_pos.top,
                                                   pos_left=app_mah_pos.left,
                                                   height=cell_height,
                                                   width=cell_width))
    grid.add(detail_bar, grid_opts=opts.GridOpts(pos_top=app_detail_pos.top,
                                                 pos_left=app_detail_pos.left,
                                                 height=cell_height,
                                                 width=cell_width))

    grid.add(detail_bar1, grid_opts=opts.GridOpts(pos_top=app_detail_pos1.top,
                                                  pos_left=app_detail_pos1.left,
                                                  height=cell_height,
                                                  width=cell_width))

    grid.render(file_name)
