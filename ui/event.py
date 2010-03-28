# coding: utf-8
import os, sys
import wx
import  wx.lib.newevent

(UpdateNotifyEvent, EVT_UPDATE_NOTIFY) = wx.lib.newevent.NewEvent()
(MyAlertEvent, EVT_MYALERT) = wx.lib.newevent.NewEvent()

