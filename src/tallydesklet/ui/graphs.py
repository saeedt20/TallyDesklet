from .theme import color, rounded


def bar(cr, x, y, width, fraction, accent, line, rtl=False):
    count, gap = 36, 2
    segment = (width - gap*(count-1))/count
    for i in range(count):
        offset = count-1-i if rtl else i
        rounded(cr, x+offset*(segment+gap), y, segment, 7, 1)
        color(cr, line, .25)
        cr.fill()
        amount = max(0, min(1, (fraction or 0)*count-i))
        if amount:
            left = x+offset*(segment+gap)+(segment*(1-amount) if rtl else 0)
            rounded(cr, left, y, segment*amount, 7, min(1, segment*amount/2))
            color(cr, accent, .95)
            cr.fill()


def graph(cr, points, now, x, y, width, height, maximum, accent, fill=False, dashed=False):
    cr.save()
    cr.rectangle(x, y, width, height)
    cr.clip()
    segments = []
    segment = []
    last = None
    for timestamp, value in points:
        if value is None or (last is not None and timestamp - last > 15):
            if segment:
                segments.append(segment)
            segment = []
        if value is not None:
            segment.append((x + width * (1 - (now-timestamp) / 60),
                            y + height * (1 - max(0, min(1, value / maximum)))))
        last = timestamp
    if segment:
        segments.append(segment)
    for segment in segments:
        if fill and len(segment) > 1:
            cr.move_to(segment[0][0], y+height)
            for point in segment:
                cr.line_to(*point)
            cr.line_to(segment[-1][0], y+height)
            cr.close_path()
            color(cr, accent, .10)
            cr.fill()
        cr.move_to(*segment[0])
        for point in segment[1:]:
            cr.line_to(*point)
        cr.set_line_width(1.5)
        if dashed:
            cr.set_dash((3, 3))
        color(cr, accent)
        cr.stroke()
    cr.restore()
