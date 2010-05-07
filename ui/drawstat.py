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
        if size.width == 0 or size.height == 0:
            return False
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


class CharDrawer (wx.Panel, ScaledBufferMixin):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        ScaledBufferMixin.__init__(self)

        self.fontsize = 9
        #self.leftspacing = 20

    def draw(self, dc, size):
        dc.SetBackground(wx.Brush("#ffffff"))
        dc.Clear()

    def draw_pie(self, data, surplus):
        self.bgcolor    = '#ffffff'
        self.data = data
        self.surplus = surplus
        self.hspacing = 100
        self.vspacing = 40

        self.colormap = []
        for x in  range(2, 20):
            self.colormap.append([x**3-x, x])
        
        self.draw = self._drawpie
        self.redraw()

    def _drawpie(self, dc, size):
        dc.SetBackground(wx.Brush(self.bgcolor))
        dc.Clear()
 
        f = wx.Font(self.fontsize, wx.FONTFAMILY_SWISS , wx.NORMAL, wx.NORMAL)
        #f.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(f)

        rect = self.GetClientRect()
        minval = min(rect.width, rect.height)
        minspacing = min(self.hspacing, self.vspacing) 
        r = (minval - self.vspacing*2) * 0.4
        x = self.hspacing + r
        y = (rect.height/2)

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
        c1 = copy.copy(colorange)
        c2 = copy.copy(colorange)
        c3 = copy.copy(colorange)

        for xr in c1:
            for xg in c2:
                for xb in c2:
                    if xr == xg == xb:
                        continue
                    colors.append((xr, xg, xb))

        sumval = 0
        for item in self.data:
            sumval += item['data']
 
        color = wx.Colour(255, 255, 255, wx.ALPHA_OPAQUE)
        dc.SetPen(wx.Pen(color))
    
        rate = 0
        lastpos = (self.x+self.r, self.y)
        for i in xrange(0, len(self.data)):
            rgb = colors[i]
            r, g, b = rgb
            #color   = wx.Colour(r, g, b, wx.ALPHA_OPAQUE)
            color   = wx.Colour(255, 255, 255, wx.ALPHA_OPAQUE)
            dc.SetPen(wx.Pen(color))
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
            if newpos[0] != lastpos[0] and newpos[1] != lastpos[1]:
                dc.DrawArc(newpos[0], newpos[1], lastpos[0], lastpos[1], self.x, self.y)
            
            jiao = 2*3.14159*(rate - ratenow/2)
            if ratenow < 0.02:
                rr = self.r + 65
            else:
                rr = self.r + 30
            frompos = [int(self.x + math.cos(jiao) * self.r), int(self.y+math.sin(jiao) * self.r)]
            textpos = [int(self.x + math.cos(jiao) * rr), int(self.y+math.sin(jiao) * rr)]
            
            color   = wx.Colour(r, g, b, wx.ALPHA_OPAQUE)
            dc.SetPen(wx.Pen(color))
            dc.DrawLine(frompos[0], frompos[1], textpos[0], textpos[1])
            
            if textpos[0] > self.x and textpos[1] < self.y:
                textpos[0] += 2
                textpos[1] -= 9
            elif textpos[0] < self.x and textpos[1] < self.y:
                textpos[0] -= 35
                textpos[1] -= 12
            elif textpos[0] < self.x and textpos[1] >= self.y:
                textpos[0] -= 35
                textpos[1] += 2

            dc.DrawText(str(round(ratenow*100, 2))+'%', textpos[0], textpos[1])    
            lastpos = newpos
            
        # display name 
        mydata = copy.copy(self.data)
        mydata.sort(key=lambda x:x['data'], reverse=True)
        
        xstart = self.hspacing*2 + self.r*2 + 50
        ystart = 20
 
        color   = wx.Colour(255, 255, 255, wx.ALPHA_OPAQUE)
        dc.SetPen(wx.Pen(color))
        
        total = sum([ k['data'] for k in mydata ])
        dc.DrawText(_('Sum: ') + str(total) ,xstart, ystart)
        dc.DrawText(_('Surplus: ') + str(self.surplus) ,xstart+100, ystart)

        ystart += 20

        for i in range(0, len(mydata)):
            ypos = ystart + i*20
            if ypos + 20 >= rect.height:
                continue
            item = mydata[i]
            dc.SetBrush(wx.Brush(item['color']))
            dc.DrawRectangle(xstart, ypos, 30, 15)
            dc.DrawText('%.2f%%  %s %d' % (round(item['rate']*100, 2), item['name'], item['data']), xstart+35, ystart+i*20)

    def draw_bar(self, data):
        self.bgcolor    = '#ffffff'
        self.linecolor  = '#eeeeee'
        self.barcolor   = ['#8d210c', '#1a6f9b', '#358335']
        self._barcolor  = []
            
        for x in self.barcolor:
            self._barcolor.append([int(x[1:3], 16), int(x[3:5], 16), int(x[5:7], 16)])

        self.spacing    = 25
        
        self.data = data
        self.draw = self._drawbar
        self.redraw()

    def _drawbar(self, dc, size):
        dc.SetBackground(wx.Brush(self.bgcolor))
        dc.Clear()

        if not self.data:
            return
 
        maxval = 0
        for item in self.data[0]:
            val = item[1]
            if val > maxval:
                maxval = val
        for item in self.data[1]:
            val = item[1]
            if val > maxval:
                maxval = val
 
        maxy = (maxval / 10 + 1) * 10
           
        f = wx.Font(self.fontsize, wx.FONTFAMILY_SWISS , wx.NORMAL, wx.NORMAL)
        #f.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(f)

        labelspacing = 65
        vspacing = 30
        leftspacing = self.spacing + labelspacing
        topspacing  = self.spacing + vspacing
        cellspacing = 10
        maxx = 24

        width  = size.width
        height = size.height

        xcount = len(self.data[0])
        ycount = 10
        xbsize = (width  - 2 * self.spacing - labelspacing) / xcount
        ybsize = (height - 2 * self.spacing - vspacing) / ycount
        xbval  = maxx / xcount
        ybval  = maxy / ycount
        
        dc.SetBrush(wx.Brush(self.linecolor))

        if xbsize < 30:
            cellspacing = int(xbsize * 0.2)

        # y
        dc.DrawLine(leftspacing, height - topspacing, leftspacing, height - topspacing - ybsize * ycount)
        # x 
        dc.DrawLine(leftspacing, height - topspacing, leftspacing + xbsize * xcount, height - topspacing)
        
        cy = height - self.spacing + 5
        #dc.DrawText(_('Time'), width/2 - 30, height - self.spacing)
        dc.DrawText(_('Time'), width/2 - 30, cy)
        cx = width/2 - 30 + 100

        ctext = [_('Income'), _('Payout'), _('Surplus')]
        for i in range(0, len(self.data)):
            penclr   = wx.Colour(self._barcolor[i][0], self._barcolor[i][1], 
                                 self._barcolor[i][2], wx.ALPHA_OPAQUE)
            dc.SetPen(wx.Pen(penclr))
            dc.SetBrush(wx.Brush(self.barcolor[i]))
 
            dc.DrawText(ctext[i], cx, cy)
            dc.DrawRectangle(cx + 30, cy, 30, 15)
            cx += 80
            
        ypos = height/2 - 30
        ystr = _('Money')
        for x in ystr:
            dc.DrawText(x, self.spacing-self.fontsize, ypos)
            ypos += self.fontsize + 5

        dc.DrawText('0', leftspacing-2, height - topspacing + 5)
        # draw y money
        for i in range(1, ycount+1):
            y = (height-topspacing) - i*ybsize 
            dc.DrawLine(leftspacing, y, leftspacing-5, y)
            dc.DrawText(str(int(i*ybval)), leftspacing-45, y-3)

        for i in range(1, xcount+1):
            x = leftspacing + i*xbsize 
            #text = self.data[i-1]['name']
            text = self.data[0][i-1][0]
            if len(text) == 6:
                text1 = text[:4]
                text2 = text[4:]
            else:
                text1 = ''
                text2 = text
            dc.DrawLine(x, height-topspacing, x, height-topspacing+5)
            #dc.DrawText(str(i), x-5, height-topspacing + 5)
            dc.DrawText(text2, x-12, height-topspacing + 5)
            dc.DrawText(text1, x-self.fontsize*3, height-topspacing + 5 + self.fontsize + 5)
         
        # draw data
        valnum = []
        for idx in range(0, len(self.data)):
            item = self.data[idx]

            penclr   = wx.Colour(self._barcolor[idx][0], self._barcolor[idx][1], 
                                 self._barcolor[idx][2], wx.ALPHA_OPAQUE)
            dc.SetPen(wx.Pen(penclr))
            dc.SetBrush(wx.Brush(self.barcolor[idx]))
 
            for i in range(0, len(item)):
                #val = self.data[i]['data']
                val = item[i][1]
                if val < 0:
                    val = 0
                w = xbsize-cellspacing+1
                x = leftspacing + i*xbsize + cellspacing
                y = height - topspacing - (float(val)/maxy) * (ybsize*ycount)
                h = height-topspacing-y+1
 
                #dc.DrawRectangle(x, y, xbsize-cellspacing+1, height-spacing-y+1)
                if w > 80:
                    cha = w - 80
                    x = x + cha
                    w = 80

                w1 = w / 3
                x1 = x + w1 * idx
                #dc.DrawRectangle(x, y, w, h)
                dc.DrawRectangle(x1, y, w1, h)
                #dc.DrawText(str(self.data[i]['data']), x, y - 20)
                #dc.DrawText(str(item[i][1]), x, y - 20)
                valnum.append([str(int(item[i][1])), x1, y - 20])
                #dc.DrawText(str(item[i][1]), x1, y - 20)

        for x in valnum:
            if x[0] != '0':
                dc.DrawText(x[0], x[1], x[2])


    def draw_table(self, data):
        self.bgcolor = '#ffffff'
        self.margin_left  = 20
        self.margin_top   = 40
        self.lineheight = 50

        self.cellpadding_top  = (self.lineheight - self.fontsize) / 2
        #self.cellpadding_left = 0
        
        self.barcolor   = ['#8d210c', '#1a6f9b', '#358335']
        self._barcolor  = []
            
        for x in self.barcolor:
            self._barcolor.append([int(x[1:3], 16), int(x[3:5], 16), int(x[5:7], 16)])


        self.data = data
        self.draw = self._drawtable
        self.redraw()

    def _drawtable(self, dc, size):
        dc.SetBackground(wx.Brush(self.bgcolor))
        dc.Clear()
        rect = self.GetClientRect()

        f = wx.Font(self.fontsize, wx.FONTFAMILY_SWISS , wx.NORMAL, wx.NORMAL)
        dc.SetFont(f)
        # 说明            
        x1 = self.margin_left
        y1 = 20
        text = [_('Income'), _('Payout'), _('Surplus')]
        for i in range(0, len(text)):
            penclr   = wx.Colour(self._barcolor[i][0], self._barcolor[i][1], 
                                 self._barcolor[i][2], wx.ALPHA_OPAQUE)
            dc.SetPen(wx.Pen(penclr))
            dc.SetBrush(wx.Brush(self.barcolor[i]))
            dc.SetTextForeground(penclr)
 
            dc.DrawText(text[i], x1, y1)
            dc.DrawRectangle(x1 + 30, y1, 30, 15)
            x1 += 80
 
        penclr   = wx.Colour(0, 0, 0, wx.ALPHA_OPAQUE)
        dc.SetPen(wx.Pen(penclr))
        dc.SetBrush(wx.Brush(self.barcolor[i]))
        dc.SetTextForeground(penclr)
        
        # 表格横线
        x1 = self.margin_left
        y1 = self.margin_top
        x2 = rect.width - self.margin_left
        y2 = y1

        for i in range(0, len(self.data) + 1):
            dc.DrawLine(x1, y1, x2, y2)
            y1 += self.lineheight
            y2 = y1
        y1 = self.margin_top + self.lineheight * (len(self.data) + 1)
        y2 = y1
        dc.DrawLine(x1, y1, x2, y2)
        
        # 表格月分割的竖线
        x1 = self.margin_left
        y1 = self.margin_top
        x2 = x1
        y2 = self.margin_top + (len(self.data) + 1) * self.lineheight + 1
        
        colsize = (rect.width - self.margin_left*2) / 14
        cellpadding_left = (colsize - 18) / 2
        for i in range(0, 14):
            dc.DrawLine(x1, y1, x2, y2)

            if i > 0 and i < 13:
                dc.DrawText(str(i) + u'月', x1 + cellpadding_left, y1 + self.cellpadding_top)

            if i == 13:
                dc.DrawText(u'总计', x1 + cellpadding_left, y1 + self.cellpadding_top)

 
            x1 += colsize
            x2 = x1

        x1 = rect.width - self.margin_left
        x2 = x1
        dc.DrawLine(x1, y1, x2, y2)
        
        # 年的字
        cellpadding_left = (colsize - 35) / 2
        x1 = self.margin_left + cellpadding_left
        y1 = self.margin_top + self.lineheight + self.cellpadding_top

        for i in range(0, len(self.data)):
            dc.DrawText(str(self.data[i][0]) + u'年', x1, y1)
            y1 += self.lineheight

        
        cellpadding_left = 5
        x1 = self.margin_left + colsize + cellpadding_left
        y1 = self.margin_top + self.lineheight + 5
        for row in self.data:
            year = row[0]
            item = row[1]
            sums = row[2]

            for monthdata in item:
                m = monthdata[0]
                vals = monthdata[1]
                
                x1 = self.margin_left + cellpadding_left + colsize * m

                x2 = x1
                y2 = y1 
                
                #for val in vals:
                for i in range(0, len(vals)):
                    val = vals[i]
                    penclr   = wx.Colour(self._barcolor[i][0], self._barcolor[i][1], 
                                         self._barcolor[i][2], wx.ALPHA_OPAQUE)
                    dc.SetTextForeground(penclr)
                
                    dc.DrawText(str(val), x2, y2)
                    y2 += 13


                x1 += colsize
            
            x2 = self.margin_left + cellpadding_left + colsize * 13
            y2 = y1
            for i in range(0, len(sums)):
                val = sums[i]
                penclr   = wx.Colour(self._barcolor[i][0], self._barcolor[i][1], 
                                     self._barcolor[i][2], wx.ALPHA_OPAQUE)
                dc.SetTextForeground(penclr)
                
                dc.DrawText(str(val), x2, y2)
                y2 += 13

            y1 += self.lineheight


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



