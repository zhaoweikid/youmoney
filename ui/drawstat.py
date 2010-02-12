# coding: utf-8
import wx
import os, string
import types
import math, copy

def _ScaleBlit(bmp, dc, dst_rect):
    if bmp.GetWidth() == 0 or bmp.GetHeight() == 0:
        return

    sX = float(dst_rect.width) / float(bmp.GetWidth())
    sY = float(dst_rect.height) / float(bmp.GetHeight())

    dc.SetUserScale(sX, sY)

    old_mode = None
    if os.name == 'nt':
        h_dst = dc.GetHDC()
        try:
            old_mode = win32gui.SetStretchBltMode(h_dst, win32con.HALFTONE)
        except:
            pass

    if sX == 0:
        w = 0
    else:
        w = dst_rect.x/sX

    if sY == 0:
        h = 0
    else:
        h = dst_rect.y/sY

    dc.DrawBitmap(bmp, w, h, True)

    if os.name == 'nt':
        try:
            win32gui.SetStretchBltMode(h_dst, old_mode)
        except:
            pass

    dc.SetUserScale(1, 1)


class DoubleBufferedMixin(object):

    def __init__(self):
        self.bind_events()
        self.buffer_size = wx.Size(-1, -1)
        self.last_size = self._calc_size()
        self.init_buffer()

    def _calc_size(self):
        return self.GetClientSize()

    def init_buffer(self):
        size = self._calc_size()
        #if ((self.buffer_size.width < size.width) or (self.buffer_size.height < size.height)):
        if ((self.buffer_size.width != size.width) or (self.buffer_size.height != size.height)):
            self.buffer = wx.EmptyBitmap(size.width, size.height)
            dc = wx.MemoryDC()
            dc.SelectObject(self.buffer)
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
            dc.Clear()
            dc.SelectObject(wx.NullBitmap)
            self.buffer_size = size
            return True
        return False

    def bind_events(self):
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e : None)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def redraw(self):
        dc = wx.MemoryDC()
        dc.SelectObject(self.buffer)
        size = self._calc_size()
        self.last_size = size
        self.draw(dc, size=size)
        dc.SelectObject(wx.NullBitmap)
        self.Refresh()

    def OnSize(self, event):
        reallocated = self.init_buffer()
        if reallocated or self.last_size != self._calc_size():
            self.redraw()
        else:
            self.Refresh()

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)

class ScaledBufferMixin(DoubleBufferedMixin):

    def __init__(self, w_step=200, h_step=15):
        self.w_step = w_step
        self.h_step = h_step
        # don't go crazy
        self.w_max = 1920
        self.h_max = 1200
        DoubleBufferedMixin.__init__(self)

    def _round(self, d, step):
        return max(int(d / step), 1) * step

    def _calc_size(self):
        size = self.GetClientSize()
        return size
        # * 2 for the high quality
        w = self._round(size.width*2, self.w_step)
        h = self._round(size.height, self.h_step)
        w = max(w, self.buffer_size.width)
        w = min(w, self.w_max)
        h = max(h, self.buffer_size.height)
        h = min(h, self.h_max)
        return wx.Size(w, h)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        _ScaleBlit(self.buffer, dc, self.GetClientRect(), strip_border=1)


class ChartBar (wx.Panel, ScaledBufferMixin):
    def __init__(self, parent, data=None):
        wx.Panel.__init__(self, parent, -1)
        ScaledBufferMixin.__init__(self)
        
        self.bgcolor    = '#ffffff'
        self.linecolor  = '#eeeeee'
        self.barcolor   = '#358e35'
        self.spacing    = 65
        
        self.data = data

        self.redraw()

    def draw(self, dc, size):
        dc.SetBackground(wx.Brush(self.bgcolor))
        dc.Clear()
 
        rect = self.GetClientRect()
        clientsize = (rect.width, rect.height)

        if not self.data:
            return
        
        maxval = 0
        vals = []
        for item in self.data:
            if type(item) == types.DictType:
                val = item['data']
            else:
                val = item
            vals.append(val)
            if val > maxval:
                maxval = val

        maxy = (maxval / 10 + 1) * 10
           
        self.fontsize = 9
        f = wx.Font(self.fontsize, wx.FONTFAMILY_SWISS , wx.NORMAL, wx.NORMAL)
        #f.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(f)

        self.draw_coordinate(dc, vals, 12, maxy, clientsize, self.spacing)


    def draw_coordinate(self, dc, values, maxx, maxy, clientsize, spacing=30):
        cellspacing = 10
        width  = clientsize[0]
        height = clientsize[1]

        xcount = len(values)
        ycount = 10
        xbsize = (width - 2 * spacing) / xcount
        ybsize = (height - 2 * spacing) / ycount
        xbval  = maxx / xcount
        ybval  = maxy / ycount
        
        dc.SetBrush(wx.Brush(self.linecolor))

        if xbsize < 30:
            cellspacing = int(xbsize * 0.2)

        #print 'xbsize:', xbsize, 'ybsize:', ybsize 
        dc.DrawLine(spacing, height - spacing, spacing, height - spacing - ybsize * ycount)
        dc.DrawLine(spacing, height - spacing, spacing + xbsize * xcount, height-spacing)
        
        dc.DrawText(u'时间', width/2 - 30, height - 20)
        ypos = height/2 - 30
        dc.DrawText(u'金', 5, ypos)
        dc.DrawText(u'额', 5, ypos + 20)

        dc.DrawText('0', spacing, height-spacing + 5)
        
        #print 'xcount:', xcount, 'ycount:', ycount
        for i in range(1, ycount+1):
            y = (height-spacing) - i*ybsize 
            dc.DrawLine(spacing, y, spacing-5, y)
            dc.DrawText(str(i*ybval), spacing-45, y-3)

        for i in range(1, xcount+1):
            x = spacing + i*xbsize 
            dc.DrawLine(x, height-spacing, x, height-spacing+5)
            dc.DrawText(str(i), x-5, height-spacing + 5)
         
        # draw data
        penclr   = wx.Colour(int(self.barcolor[1:3], 16), int(self.barcolor[3:5], 16), 
                             int(self.barcolor[5:7], 16), wx.ALPHA_OPAQUE)
        dc.SetPen(wx.Pen(penclr))
        dc.SetBrush(wx.Brush(self.barcolor))
        for i in range(0, len(values)):
            val = values[i]
            x = spacing + i*xbsize + cellspacing
            y = height - spacing - (float(val)/maxy) * (ybsize*ycount)
            dc.DrawRectangle(x, y, xbsize-cellspacing+1, height-spacing-y+1)
            dc.DrawText(str(val), x, y - 20)


    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        rect = self.GetClientRect()
        _ScaleBlit(self.buffer, dc, rect)

class ChartPie (wx.Panel, ScaledBufferMixin):
    #def __init__(self, parent, x, y, r, data=None):
    def __init__(self, parent, data=None):
        '''data - {'data':xxx, 'name':xxx}
        '''
        wx.Panel.__init__(self, parent, -1)
        ScaledBufferMixin.__init__(self)
        
        self.bgcolor    = '#ffffff'
        self.data = data
        self.spacing = 60

        #self.x = x
        #self.y = y
        #self.r = r

        self.colormap = []

        for x in  range(2, 20):
            self.colormap.append([x**3-x, x])

        self.redraw()

    def draw(self, dc, size):
        dc.SetBackground(wx.Brush(self.bgcolor))
        dc.Clear()
 
        rect = self.GetClientRect()
        minval = min(rect.width, rect.height)
        
        r = (minval - self.spacing*2) * 0.4
        x = self.spacing + r
        y = (rect.height/2)

        #print x, y, r, minval

        self.x = x
        self.y = y
        self.r = r
 

        clientsize = (rect.width, rect.height)
        
        size = len(self.data)
       
        n = 0
        for x in self.colormap:
            if x[0] > size:
                n = x[1]
                break

        colors = []
        colorange = []
        nsize = int(255.0 / n)
        for xi in xrange(0, n):
            colorange.append(nsize * xi)
        #print 'colorange:', colorange
        c1 = copy.copy(colorange)
        c2 = copy.copy(colorange)
        c3 = copy.copy(colorange)

        for xr in c1:
            for xg in c2:
                for xb in c2:
                    if xr == xg == xb:
                        continue
                    #print xr, xg, xb
                    colors.append((xr, xg, xb))
        #print 'colors:', colors

        sumval = 0
        for item in self.data:
            sumval += item['data']
 
        color   = wx.Colour(255, 255, 255, wx.ALPHA_OPAQUE)
        dc.SetPen(wx.Pen(color))
    
        rate = 0
        lastpos = (self.x+self.r, self.y)
        for i in xrange(0, len(self.data)):
            rgb = colors[i]
            r, g, b = rgb
            #color   = wx.Colour(r, g, b, wx.ALPHA_OPAQUE)
            #color   = wx.Colour(255, 255, 255, wx.ALPHA_OPAQUE)
            #dc.SetPen(wx.Pen(color))
            colorstr = '#'
            for ci in rgb:
                cs1 = hex(ci)[2:]
                if len(cs1) == 1:
                    cs1 = '0' + cs1
                colorstr += cs1
            #print 'colorstr:', colorstr
            #brush = wx.Brush(colorstr)
            #brush.SetCoulor(color)
            dc.SetBrush(wx.Brush(colorstr))

            item = self.data[i]
            item['color'] = colorstr
            ratenow = float(item['data']) / sumval
            item['rate'] = ratenow
            rate = rate + ratenow

            jiao = 2*3.14159*rate
            newpos = (int(self.x + math.cos(jiao) * self.r), int(self.y+math.sin(jiao) * self.r))

            #print 'last:', lastpos, 'new:', newpos, 'rate:', rate
            #dc.DrawArc(lastpos[0], lastpos[1], newpos[0], newpos[1], self.x, self.y)
            dc.DrawArc(newpos[0], newpos[1], lastpos[0], lastpos[1], self.x, self.y)
            
            jiao = 2*3.14159*(rate - ratenow/2)
            textpos = [int(self.x + math.cos(jiao) * self.r), int(self.y+math.sin(jiao) * self.r)]

            if textpos[0] < self.x:
                textpos[0] = textpos[0] - 60

            if textpos[1] < self.y:
                textpos[1] -= 20

            dc.DrawText(str(round(ratenow*100, 2))+'%', textpos[0], textpos[1])    
            lastpos = newpos
            
        # display name 
        mydata = copy.copy(self.data)
        mydata.sort(key=lambda x:x['data'], reverse=True)
        
        xstart = self.spacing*2 + self.r*2
        ystart = self.spacing
        
        for i in range(0, len(mydata)):
            item = mydata[i]
            dc.SetBrush(wx.Brush(item['color']))
            dc.DrawRectangle(xstart, ystart+i*20, 30, 15)
            dc.DrawText('%d %.2f%%  ' % (item['data'], round(item['rate']*100, 2))  + item['name'], xstart+35, ystart+i*20)


    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        rect = self.GetClientRect()
        _ScaleBlit(self.buffer, dc, rect)


   

def test(parent):
    data = [109900, 2378, 5231, 1771, 3499, 1000, 2342, 9982, 8283, 12314, 46786, 7863, 
            12312, 21222, 1234, 1231, 1415, 5326, 4266, 2134, 21314, 21313,
            12312, 21222, 1234, 1231, 1415, 5326, 4266]
    #win = ChartBar(parent, data)
    data = [{'data':120, 'name':'a111'}, {'data':324, 'name':'b222'}, 
            {'data':123, 'name':'c231'}, {'data':325, 'name':'d8989'},
            {'data':524, 'name':u'测试1'}, {'data':800, 'name':u'发财了'},
            {'data':233, 'name':u'呵呵'}, {'data':122, 'name':u'哈哈'}]
    #win = ChartPie(nb, 300, 200, 100, data)
    win = ChartPie(parent, data)
    return win



