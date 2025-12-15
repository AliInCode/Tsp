import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import folium
from folium import plugins
import webbrowser
import os
from geopy.distance import geodesic
from ttkthemes import ThemedTk

# تعریف مختصات جغرافیایی محله‌های ساری (طول و عرض جغرافیایی)
neighborhoods_coords = {
    "میدان ساعت": {"lat": 36.5631, "lon": 53.0581},
    "پردیس": {"lat": 36.5689, "lon": 53.0633},
    "کوی ندا": {"lat": 36.5712, "lon": 53.0667},
    "کوی طلاب": {"lat": 36.5655, "lon": 53.0611},
    "کوی امام": {"lat": 36.5678, "lon": 53.0644},
    "کوی مهدی": {"lat": 36.5701, "lon": 53.0678},
    "کوی ولیعصر": {"lat": 36.5724, "lon": 53.0711},
    "کوی آزادگان": {"lat": 36.5747, "lon": 53.0744},
    "کوی شاهد": {"lat": 36.5770, "lon": 53.0778},
    "کوی شهید رجایی": {"lat": 36.5793, "lon": 53.0811},
    "کوی شهید بهشتی": {"lat": 36.5816, "lon": 53.0844},
    "کوی شهید مطهری": {"lat": 36.5839, "lon": 53.0878},
    "کوی شهید باهنر": {"lat": 36.5862, "lon": 53.0911},
    "کوی شهید رجایی ۲": {"lat": 36.5885, "lon": 53.0944},
    "کوی شهید بهشتی ۲": {"lat": 36.5908, "lon": 53.0978}
}

# محاسبه فاصله واقعی بین محله‌ها (به متر)
def calculate_distance(coord1, coord2):
    return geodesic(
        (coord1["lat"], coord1["lon"]),
        (coord2["lat"], coord2["lon"])
    ).meters

# تعریف گراف محله‌ها و مسیرها با فاصله واقعی
graph = {}
for neighborhood1, coords1 in neighborhoods_coords.items():
    graph[neighborhood1] = []
    for neighborhood2, coords2 in neighborhoods_coords.items():
        if neighborhood1 != neighborhood2:
            # فقط محله‌های نزدیک به هم را به هم متصل می‌کنیم (کمتر از 1 کیلومتر)
            distance = calculate_distance(coords1, coords2)
            if distance < 1000:  # 1 کیلومتر
                graph[neighborhood1].append((neighborhood2, round(distance)))

def dijkstra(start, end):
    """الگوریتم دایکسترا برای پیدا کردن کوتاه‌ترین مسیر"""
    queue = [(0, start, [])]
    visited = set()
    
    while queue:
        (cost, current, path) = heapq.heappop(queue)
        if current in visited:
            continue
        visited.add(current)
        path = path + [current]
        
        if current == end:
            return path, cost
            
        for (neighbor, weight) in graph.get(current, []):
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path))
    
    return None, None

class MapShortestPathApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نقشه کوتاه‌ترین مسیر محله‌های ساری")
        self.root.geometry("1000x700")
        
        # تنظیم تم و رنگ‌ها
        self.style = ttk.Style()
        self.style.theme_use('equilux')  # استفاده از تم equilux
        
        # تنظیم رنگ‌های سفارشی
        self.style.configure('TFrame', background='#2b2b2b')
        self.style.configure('TLabel', background='#2b2b2b', foreground='#ffffff', font=('Tahoma', 12))
        self.style.configure('TButton', 
                           background='#404040', 
                           foreground='#ffffff',
                           font=('Tahoma', 11, 'bold'),
                           padding=10)
        self.style.map('TButton',
                      background=[('active', '#505050'), ('pressed', '#606060')],
                      foreground=[('active', '#ffffff')])
        self.style.configure('TCombobox',
                           fieldbackground='#404040',
                           background='#404040',
                           foreground='#ffffff',
                           arrowcolor='#ffffff',
                           font=('Tahoma', 11))
        self.style.map('TCombobox',
                      fieldbackground=[('readonly', '#404040')],
                      selectbackground=[('readonly', '#505050')])
        
        # تنظیم رنگ پس‌زمینه اصلی
        self.root.configure(bg='#2b2b2b')
        
        # ایجاد فریم اصلی با پدینگ بیشتر
        main_frame = ttk.Frame(root, padding="20", style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # عنوان برنامه
        title_label = ttk.Label(main_frame, 
                              text="نقشه هوشمند محله‌های ساری",
                              font=('Tahoma', 16, 'bold'),
                              style='TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # لیست محله‌ها
        neighborhoods = list(graph.keys())
        
        # فریم انتخاب محله‌ها با استایل جدید
        input_frame = ttk.Frame(main_frame, style='TFrame')
        input_frame.grid(row=1, column=0, columnspan=2, pady=20, sticky='ew')
        
        # انتخاب محله مبدأ
        ttk.Label(input_frame, 
                 text="محله مبدأ:",
                 font=('Tahoma', 12, 'bold'),
                 style='TLabel').grid(row=0, column=0, padx=10)
        self.start_neighborhood = ttk.Combobox(input_frame, 
                                             values=neighborhoods,
                                             state="readonly",
                                             width=30,
                                             font=('Tahoma', 11))
        self.start_neighborhood.grid(row=0, column=1, padx=10)
        
        # انتخاب محله مقصد
        ttk.Label(input_frame,
                 text="محله مقصد:",
                 font=('Tahoma', 12, 'bold'),
                 style='TLabel').grid(row=0, column=2, padx=10)
        self.end_neighborhood = ttk.Combobox(input_frame,
                                           values=neighborhoods,
                                           state="readonly",
                                           width=30,
                                           font=('Tahoma', 11))
        self.end_neighborhood.grid(row=0, column=3, padx=10)
        
        # دکمه‌های عملیات با استایل جدید
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        show_path_btn = ttk.Button(button_frame,
                                 text="نمایش مسیر",
                                 command=self.show_path,
                                 style='TButton',
                                 width=20)
        show_path_btn.grid(row=0, column=0, padx=10)
        
        show_map_btn = ttk.Button(button_frame,
                                text="نمایش نقشه",
                                command=self.show_map,
                                style='TButton',
                                width=20)
        show_map_btn.grid(row=0, column=1, padx=10)
        
        # فریم نتیجه با استایل جدید
        result_frame = ttk.Frame(main_frame, style='TFrame')
        result_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky='ew')
        
        self.result_label = ttk.Label(result_frame,
                                    text="",
                                    wraplength=900,
                                    font=('Tahoma', 12),
                                    style='TLabel',
                                    justify='center')
        self.result_label.grid(row=0, column=0, pady=10)
        
        # تنظیم وزن ستون‌ها برای مرکزسازی
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # ذخیره مسیر فعلی
        self.current_path = None
        self.current_cost = None

    def show_path(self):
        start = self.start_neighborhood.get()
        end = self.end_neighborhood.get()
        
        if not start or not end:
            self.result_label.config(text="⚠️ لطفاً هر دو محله را انتخاب کنید.")
            return
            
        if start == end:
            self.result_label.config(text="⚠️ محله مبدأ و مقصد نمی‌توانند یکسان باشند.")
            return
        
        # محاسبه مسیر جدید
        path, cost = dijkstra(start, end)
        
        if path:
            self.current_path = path
            self.current_cost = cost
            result_text = f"📍 کوتاه‌ترین مسیر:\n{' → '.join(path)}\n\n🚗 مسافت کل: {cost/1000:.1f} کیلومتر"
        else:
            self.current_path = None
            self.current_cost = None
            result_text = "❌ مسیری بین این دو محله یافت نشد."
        
        self.result_label.config(text=result_text)
    
    def show_map(self):
        if not self.current_path:
            messagebox.showwarning("هشدار", "لطفاً ابتدا یک مسیر را محاسبه کنید.")
            return
            
        # ایجاد نقشه با مرکزیت ساری
        m = folium.Map(location=[36.5631, 53.0581], zoom_start=14)
        
        # اضافه کردن نشانگر برای محله‌های مسیر
        for i, neighborhood in enumerate(self.current_path):
            coords = neighborhoods_coords[neighborhood]
            color = 'red' if i == 0 or i == len(self.current_path)-1 else 'blue'
            folium.Marker(
                location=[coords["lat"], coords["lon"]],
                popup=neighborhood,
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)
        
        # رسم خط مسیر
        route_coords = [neighborhoods_coords[n] for n in self.current_path]
        folium.PolyLine(
            locations=[[c["lat"], c["lon"]] for c in route_coords],
            color='red',
            weight=3,
            opacity=0.8
        ).add_to(m)
        
        # اضافه کردن کنترل‌های نقشه
        plugins.Fullscreen().add_to(m)
        plugins.MousePosition().add_to(m)
        
        # ذخیره نقشه
        map_file = "sari_route.html"
        m.save(map_file)
        
        # باز کردن نقشه در مرورگر
        webbrowser.open('file://' + os.path.realpath(map_file))

if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    app = MapShortestPathApp(root)
    root.mainloop()