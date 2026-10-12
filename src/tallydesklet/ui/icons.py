"""Original outline symbols with a shared 24-unit grid."""
from gi.repository import GdkPixbuf,Gtk
PATHS = {
 'gear':'<path d="M9 3h6l.5 3 2 1.2 2.8-1 3 5.2-2.4 2 .1 2.3 2.4 1.9-3 5.2-2.8-1-2 1.2-.5 3H9l-.5-3-2-1.2-2.8 1-3-5.2 2.4-1.9.1-2.3-2.4-2 3-5.2 2.8 1 2-1.2z" transform="translate(2 0) scale(.83)"/><circle cx="12" cy="12" r="3"/>',
 'appearance':'<circle cx="12" cy="12" r="9"/><path d="M12 3v18a9 9 0 0 1 0-18"/>',
 'language':'<rect x="3" y="4" width="18" height="16" rx="3"/><path d="m6 16 3-8 3 8m-5-3h4m4-5h3m-1.5 0v8m-1.5 0h3"/>',
 'monitor':'<path d="M3 17h3l3-10 4 13 3-8 2 5h3"/><path d="M3 4h18"/>',
 'desktop':'<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8m-4-4v4"/>',
 'bell':'<path d="M5 17h14l-2-3V9a5 5 0 0 0-10 0v5zM10 20h4"/>',
 'info':'<circle cx="12" cy="12" r="9"/><path d="M12 10v7m0-11v1"/>',
}

def symbol(name,tint,size=18):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24"><g fill="none" stroke="{tint}" stroke-width="1.65" stroke-linejoin="round" stroke-linecap="round">{PATHS[name]}</g></svg>'
    loader=GdkPixbuf.PixbufLoader.new_with_type('svg')
    loader.write(svg.encode())
    loader.close()
    return Gtk.Image.new_from_pixbuf(loader.get_pixbuf())
