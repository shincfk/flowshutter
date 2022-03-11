# Flowshutter
# Copyright (C) 2021  Hugo Chiang

# Flowshutter is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Flowshutter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with flowshutter.  If not, see <https://www.gnu.org/licenses/>.
import wlan,battery, buttons,oled, vars, json, settings, sony_multiport

welcome_time_count = 0
udpate_count = 0

def update(t):          # UI tasks controller
    battery.read_vol()  # read the battery voltage
    buttons.check(t)    # check the buttons
    _check_oled_()      # check if OLED needs update
    _check_shutter_state_() # check working state and assign handler
    _check_oled_()      # check if OLED needs update

def _check_oled_():# check if we need to update the OLED
    global udpate_count
    if udpate_count >=1000:
        udpate_count = 0
        vars.oled_need_update = "yes"
    else:
        udpate_count = udpate_count +5
    if vars.previous_state != vars.shutter_state:
        vars.previous_state = vars.shutter_state
        vars.info = vars.shutter_state
        oled.update(vars.info)
    if vars.oled_need_update == "yes":
        vars.oled_need_update = "no"
        oled.update(vars.info)

def _check_shutter_state_():
    if vars.shutter_state == "welcome":
        _welcome_()
    elif vars.shutter_state == "idle":
        _idle_()
    elif vars.shutter_state == "starting":
        _starting_()
    elif vars.shutter_state == "recording":
        _recording_()
    elif vars.shutter_state == "stopping":
        _stopping_()
    elif vars.shutter_state == "battery":
        _battery_()
    elif vars.shutter_state == "menu_internet":
        _menu_internet_() 
    elif vars.shutter_state == "menu_ota_source":
        _menu_ota_source_()
    elif vars.shutter_state == "menu_ota_channel":
        _menu_ota_channel_()
    elif vars.shutter_state == "menu_camera_protocol":
        _menu_camera_protocol_()
    elif vars.shutter_state == "menu_device_mode":
        _menu_device_mode_()
    elif vars.shutter_state == "menu_inject_mode":
        _menu_inject_mode_()
    else:
        print("Unknown UI state")

def _welcome_():
    global welcome_time_count

    # enter do nothing
    if vars.button_enter == "pressed":
        vars.button_enter = "released"
    
    # page do nothing
    if vars.button_page == "pressed":
        vars.button_page = "released"

    # welcome auto switch
    if welcome_time_count <= 2500:
        welcome_time_count = welcome_time_count + 5
    else:
        vars.shutter_state = "idle"

def _idle_():

    # enter to start recording if in master or master/slave mode
    if vars.button_enter == "pressed":
        vars.button_enter = "released"
        _rec_enter_()

    ## page to battery menu
    if vars.button_page == "pressed":
        vars.button_page = "released"
        vars.shutter_state = "battery"

def _starting_():

    # enter do nonthing
    if vars.button_enter == "pressed":
        vars.button_enter = "released"
    
    # page do nonthing
    if vars.button_page == "pressed":
        vars.button_page = "released"

def _recording_():
    
    # enter to stop recording if in master or master/slave mode
    if vars.button_enter == "pressed":
        vars.button_enter = "released"
        _rec_enter_()
    # page cicle between rec_battery and recording
    if vars.button_page == "pressed":
        vars.button_page = "released"
        _rec_page_()

def _stopping_():

    # enter do nothing
    if vars.button_enter == "pressed":
        vars.button_enter = "released"
    
    # page do nothing
    if vars.button_page == "pressed":
        vars.button_page = "released"

def _battery_():

    # page to camera protocol menu
    if vars.button_page == "pressed":
        vars.button_page = "released"
        vars.shutter_state = "menu_camera_protocol"
        vars.oled_need_update = "yes"
    
    # enter to hidden wlan mode menu
    if vars.button_enter == "pressed":
        vars.button_enter = "released"       
        vars.shutter_state = "menu_internet"
        vars.oled_need_update = "yes"

def _menu_internet_():

    # enter to set wlan up or down
    if vars.button_enter == "pressed":
        vars.button_enter = "released"
        if vars.wlan_state == "DISCONNECTED":
            wlan.up()
            vars.oled_need_update = "yes"
        else:
            wlan.down()
            vars.oled_need_update = "yes"

    ## page button
    if vars.button_page == "pressed":
        vars.button_page = "released"
        if vars.wlan_state == "CONNECTED":
            vars.shutter_state = "menu_ota_source"
        else:
            vars.shutter_state = "battery"

def _menu_ota_source_():

    # enter to set wlan up or down
    if vars.button_enter == "pressed":
        vars.button_enter = "released"
        vars.ota_source = vars.next(vars.ota_source_range, vars.ota_source)
        vars.oled_need_update = "yes"
        settings.update()

    ## page to ota channel menu
    if vars.button_page == "pressed":
        vars.button_page = "released"
        vars.shutter_state = "menu_ota_channel"

def _menu_ota_channel_():

    # enter to set ota channel
    if vars.button_enter == "pressed":
        vars.button_enter = "released"
        vars.ota_channel = vars.next(vars.ota_channel_range, vars.ota_channel)
        vars.oled_need_update = "yes"
        settings.update()

    ## page to back to battery menu
    if vars.button_page == "pressed":
        vars.button_page = "released"
        vars.shutter_state = "battery"

def _menu_camera_protocol_():

    # enter to set camera protocol
    if vars.button_enter == "pressed":
        vars.button_enter = "released"
        vars.camera_protocol = vars.next(vars.camera_protocol_range, vars.camera_protocol)
        vars.update_camera_preset()
        vars.oled_need_update = "yes"
        settings.update()

    # page to device mode
    if vars.button_page == "pressed":
        vars.button_page = "released"
        vars.shutter_state = "menu_device_mode"

def _menu_device_mode_():

    # enter to set device mode
    if vars.button_enter == "pressed":
        vars.button_enter = "released"
        vars.device_mode = vars.next(vars.device_mode_range, vars.device_mode)
        vars.oled_need_update = "yes"
        settings.update()

    # page to inject mode menu
    if vars.button_page == "pressed":
        vars.button_page = "released"       
        vars.shutter_state = "menu_inject_mode"

def _menu_inject_mode_():

    # enter to set inject mode
    if vars.button_enter == "pressed":
        vars.button_enter = "released"
        vars.inject_mode = vars.next(vars.inject_mode_range, vars.inject_mode)
        vars.oled_need_update = "yes"
        settings.update()

    ## page to save and back to idle
    if vars.button_page == "pressed":
        vars.button_page = "released"
        vars.shutter_state = "idle"

def _rec_enter_():
    if (vars.camera_protocol == "Sony MTP") & (vars.device_mode == "MASTER/SLAVE"):
        sony_multiport.uart2.write(sony_multiport.REC_PRESS)
        sony_multiport.uart2.write(sony_multiport.REC_RELEASE)
        if vars.shutter_state == "idle":
            vars.shutter_state = "starting"
        elif vars.shutter_state == "recording":
            vars.shutter_state = "stopping"
    elif (vars.camera_protocol == "NO") & (vars.device_mode == "MASTER"):
        if vars.shutter_state == "idle":
            vars.shutter_state = "recording"
            vars.arm_state = "arm"
        elif vars.shutter_state == "recording":
            vars.shutter_state = "idle"
            vars.arm_state = "disarm"

def _rec_page_():
    if vars.info == "recording":
        vars.info = "battery"
        vars.oled_need_update = "yes"
    elif vars.info == "battery":
        vars.info = "recording"
        vars.oled_need_update = "yes"
