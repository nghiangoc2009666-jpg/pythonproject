import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# 1. KHỞI TẠO CƠ SỞ DỮ LIỆU
# ==========================================
def setup_database():
    conn = sqlite3.connect('hethong_banhang_v3.db')
    cursor = conn.cursor()
    
    # Bảng Sản phẩm
    cursor.execute('''CREATE TABLE IF NOT EXISTS SanPham (
                        MaSP INTEGER PRIMARY KEY, 
                        TenSP TEXT, 
                        Gia REAL, 
                        SoLuongKho INTEGER)''')
    
    # Bảng Đơn hàng
    cursor.execute('''CREATE TABLE IF NOT EXISTS DonHang (
                        MaDH INTEGER PRIMARY KEY AUTOINCREMENT, 
                        TenKH TEXT, 
                        NgayDat TEXT, 
                        TrangThai TEXT,
                        TamTinh REAL, 
                        GiamGia REAL, 
                        Thue REAL, 
                        TongTien REAL)''')
    
    # Bảng Chi tiết đơn hàng
    cursor.execute('''CREATE TABLE IF NOT EXISTS ChiTietDonHang (
                        MaDH INTEGER, 
                        MaSP INTEGER, 
                        SoLuong INTEGER,
                        FOREIGN KEY(MaDH) REFERENCES DonHang(MaDH),
                        FOREIGN KEY(MaSP) REFERENCES SanPham(MaSP))''')

    # Bảng Voucher
    cursor.execute('''CREATE TABLE IF NOT EXISTS Voucher (
                        MaVoucher TEXT PRIMARY KEY, 
                        MoTa TEXT, 
                        GiamGia REAL, 
                        LoaiGiam TEXT, 
                        SoLuong INTEGER)''')

    # Bảng Ví Voucher của Khách hàng
    cursor.execute('''CREATE TABLE IF NOT EXISTS ViVoucher (
                        TenKH TEXT, 
                        MaVoucher TEXT, 
                        TrangThai TEXT DEFAULT 'CHUA_SU_DUNG',
                        PRIMARY KEY (TenKH, MaVoucher))''')
    
    conn.commit()
    conn.close()

# ==========================================
# 2. GIAO DIỆN ĐĂNG NHẬP
# ==========================================
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Đăng nhập hệ thống")
        self.root.geometry("380x250")
        self.root.eval('tk::PlaceWindow . center')
        
        tk.Label(self.root, text="HỆ THỐNG BÁN HÀNG TRỰC TUYẾN", font=("Arial", 12, "bold"), fg="#2c3e50").pack(pady=15)
        
        frame_input = tk.Frame(self.root)
        frame_input.pack(pady=10)
        
        tk.Label(frame_input, text="Họ và tên:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_name = ttk.Entry(frame_input, width=25)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_input, text="Loại tài khoản:", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_role = ttk.Combobox(frame_input, values=["Khách hàng", "Nhân viên"], state="readonly", width=22)
        self.combo_role.current(0)
        self.combo_role.grid(row=1, column=1, padx=5, pady=5)
        
        btn_login = tk.Button(self.root, text="Vào Hệ Thống", command=self.login,
                              bg="#27ae60", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5)
        btn_login.pack(pady=15)

    def login(self):
        name = self.entry_name.get().strip()
        role = self.combo_role.get()
        if not name:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên người sử dụng!")
            return
            
        self.root.destroy()
        main_root = tk.Tk()
        ShoppingApp(main_root, user_name=name, user_role=role)
        main_root.mainloop()

# ==========================================
# 3. GIAO DIỆN CHÍNH ỨNG DỤNG
# ==========================================
class ShoppingApp:
    def __init__(self, root, user_name, user_role):
        self.root = root
        self.user_name = user_name
        self.user_role = user_role
        self.root.title(f"Hệ Thống Bán Hàng - [{self.user_role.upper()}: {self.user_name}]")
        self.root.geometry("1000x780")
        
        self.gio_hang = []
        self.VAT_RATE = 0.10

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background="#d1d8e0")
        style.configure("Treeview", rowheight=25, font=('Arial', 10))

        # Header bar
        header = tk.Frame(self.root, bg="#34495e", pady=8)
        header.pack(fill=tk.X)
        tk.Label(header, text=f"Xin chào: {self.user_name} ({self.user_role})", 
                 font=("Arial", 11, "bold"), fg="white", bg="#34495e").pack(side=tk.LEFT, padx=15)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tab_dathang = ttk.Frame(self.notebook)
        self.tab_thanhtoan = ttk.Frame(self.notebook)
        self.tab_lichsu = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_dathang, text="  🛒 ĐẶT HÀNG MỚI  ")
        
        if self.user_role == "Khách hàng":
            self.tab_sanvoucher = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_sanvoucher, text="  🎟️ SĂN VOUCHER  ")
            self.build_tab_sanvoucher()

        self.notebook.add(self.tab_thanhtoan, text="  ⏳ CHỜ THANH TOÁN  ")
        self.notebook.add(self.tab_lichsu, text="  📜 LỊCH SỬ ĐƠN HÀNG  ")
        
        if self.user_role == "Nhân viên":
            self.tab_quanly = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_quanly, text="  ⚙️ QUẢN LÝ (NV)  ")
            self.build_tab_quanly_nv()

        self.build_tab_dathang()
        self.build_tab_thanhtoan()
        self.build_tab_lichsu()
        
        self.load_san_pham_kho()
        self.load_cho_thanh_toan()
        self.load_danh_sach_lich_su()

    def Lay_Ma_Don_Hang(self, text_combobox):
        if not text_combobox or '#' not in text_combobox:
            return None
        return text_combobox.split('#')[1].split(' ')[0].strip()

    # ------------------------------------------
    # TAB: SĂN VOUCHER (KHÁCH HÀNG)
    # ------------------------------------------
    def build_tab_sanvoucher(self):
        frame_voucher = ttk.LabelFrame(self.tab_sanvoucher, text=" Kho Mã Giảm Giá Khả Dụng ")
        frame_voucher.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = ("Mã Voucher", "Mô Tả", "Loại Giảm", "Giá Trị Giảm", "Số Lượng Còn")
        self.tree_vouchers = ttk.Treeview(frame_voucher, columns=cols, show="headings", height=8)
        for c in cols: self.tree_vouchers.heading(c, text=c)
        self.tree_vouchers.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_san = tk.Button(self.tab_sanvoucher, text="🎁 SĂN VOUCHER (LƯU VÀO VÍ)", command=self.san_voucher,
                            bg="#e67e22", fg="white", font=("Arial", 10, "bold"), padx=15, pady=6)
        btn_san.pack(pady=10)
        self.load_danh_sach_voucher()

    def load_danh_sach_voucher(self):
        for item in self.tree_vouchers.get_children(): self.tree_vouchers.delete(item)
        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MaVoucher, MoTa, LoaiGiam, GiamGia, SoLuong FROM Voucher WHERE SoLuong > 0")
        for r in cursor.fetchall():
            loai = "Phần trăm (%)" if r[2] == 'PERCENT' else "Số tiền (VNĐ)"
            gt = f"{r[3]:,.0f}%" if r[2] == 'PERCENT' else f"{r[3]:,.0f} VNĐ"
            self.tree_vouchers.insert("", tk.END, values=(r[0], r[1], loai, gt, r[4]))
        conn.close()

    def san_voucher(self):
        selected = self.tree_vouchers.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn 1 Voucher để săn!")
            return
        
        ma_voucher = self.tree_vouchers.item(selected[0], 'values')[0]
        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO ViVoucher (TenKH, MaVoucher) VALUES (?, ?)", (self.user_name, ma_voucher))
            cursor.execute("UPDATE Voucher SET SoLuong = SoLuong - 1 WHERE MaVoucher = ?", (ma_voucher,))
            conn.commit()
            messagebox.showinfo("Thành công", f"🎉 Bạn đã lưu Voucher [{ma_voucher}] vào ví!")
            self.load_danh_sach_voucher()
            self.load_vi_voucher_cb()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Thông báo", "⚠️ Bạn đã săn Voucher này rồi!")
        finally:
            conn.close()

    # ------------------------------------------
    # TAB 1: ĐẶT HÀNG MỚI
    # ------------------------------------------
    def build_tab_dathang(self):
        frame_kho = ttk.LabelFrame(self.tab_dathang, text=" Danh sách sản phẩm ")
        frame_kho.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        cols_kho = ("Mã SP", "Tên Sản Phẩm", "Đơn Giá", "Tồn Kho")
        self.tree_kho = ttk.Treeview(frame_kho, columns=cols_kho, show="headings", height=3)
        for col in cols_kho: self.tree_kho.heading(col, text=col)
        self.tree_kho.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        frame_add = ttk.Frame(frame_kho)
        frame_add.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(frame_add, text="Số lượng mua:").pack(side=tk.LEFT, padx=5)
        self.entry_soluong = ttk.Entry(frame_add, width=10)
        self.entry_soluong.pack(side=tk.LEFT, padx=5)
        btn_them = tk.Button(frame_add, text="➕ Thêm vào giỏ", command=self.them_vao_gio_hang, bg="#2980b9", fg="white")
        btn_them.pack(side=tk.LEFT, padx=10)

        frame_gio = ttk.LabelFrame(self.tab_dathang, text=" Giỏ hàng tạm thời ")
        frame_gio.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        cols_gio = ("STT", "Mã SP", "Tên Sản Phẩm", "Đơn Giá", "Số Lượng", "Thành Tiền")
        self.tree_gio = ttk.Treeview(frame_gio, columns=cols_gio, show="headings", height=3)
        for col in cols_gio: self.tree_gio.heading(col, text=col)
        self.tree_gio.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        frame_cart_action = ttk.Frame(frame_gio)
        frame_cart_action.pack(fill=tk.X, padx=5, pady=5)
        btn_xoa = tk.Button(frame_cart_action, text="🗑️ Xóa khỏi giỏ", command=self.xoa_khoi_gio_hang, bg="#e74c3c", fg="white")
        btn_xoa.pack(side=tk.LEFT, padx=5)

        ttk.Label(frame_cart_action, text="Chọn Voucher:").pack(side=tk.LEFT, padx=10)
        self.combo_voucher = ttk.Combobox(frame_cart_action, width=25, state="readonly")
        self.combo_voucher.pack(side=tk.LEFT, padx=5)
        self.combo_voucher.bind("<<ComboboxSelected>>", lambda e: self.cap_nhat_gio_hang_gui())
        
        self.lbl_tamtinh = tk.Label(frame_cart_action, text="Tạm tính: 0 VNĐ | Giảm: 0 VNĐ | Thuế (10%): 0 VNĐ | TỔNG: 0 VNĐ", 
                                    font=("Arial", 10, "bold"), fg="#27ae60")
        self.lbl_tamtinh.pack(side=tk.RIGHT, padx=10)

        frame_checkout = ttk.Frame(self.tab_dathang)
        frame_checkout.pack(fill=tk.X, padx=10, pady=5)
        btn_xacnhan = tk.Button(frame_checkout, text="📋 TẠO ĐƠN HÀNG (CHỜ THANH TOÁN)", command=self.tao_don_hang_cho,
                                bg="#27ae60", fg="white", font=("Arial", 10, "bold"), padx=15, pady=6)
        btn_xacnhan.pack(side=tk.RIGHT, padx=10)
        
        self.load_vi_voucher_cb()

    def load_vi_voucher_cb(self):
        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        cursor.execute("""SELECT v.MaVoucher, v.MoTa FROM ViVoucher vi 
                          JOIN Voucher v ON vi.MaVoucher = v.MaVoucher 
                          WHERE vi.TenKH = ? AND vi.TrangThai = 'CHUA_SU_DUNG'""", (self.user_name,))
        rows = cursor.fetchall()
        conn.close()
        
        vals = ["Không dùng Voucher"] + [f"{r[0]} - {r[1]}" for r in rows]
        self.combo_voucher['values'] = vals
        self.combo_voucher.current(0)

    def load_san_pham_kho(self):
        for item in self.tree_kho.get_children(): self.tree_kho.delete(item)
        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MaSP, TenSP, Gia, SoLuongKho FROM SanPham")
        for r in cursor.fetchall():
            self.tree_kho.insert("", tk.END, values=(r[0], r[1], f"{r[2]:,.0f} VNĐ", r[3]))
        conn.close()

    def them_vao_gio_hang(self):
        selected = self.tree_kho.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn 1 sản phẩm!")
            return
            
        vals = self.tree_kho.item(selected[0], 'values')
        ma_sp = int(vals[0])
        ten_sp = vals[1]
        gia = float(vals[2].replace(" VNĐ", "").replace(",", ""))
        ton_kho = int(vals[3])

        try:
            soluong = int(self.entry_soluong.get().strip())
            if soluong <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng phải là số nguyên dương (>0)!")
            return

        soluong_da_co = sum(item['so_luong'] for item in self.gio_hang if item['ma_sp'] == ma_sp)
        if (soluong_da_co + soluong) > ton_kho:
            messagebox.showerror("Hết hàng", f"Trong kho chỉ còn {ton_kho} sản phẩm!")
            return

        for item in self.gio_hang:
            if item['ma_sp'] == ma_sp:
                item['so_luong'] += soluong
                item['thanh_tien'] = item['so_luong'] * gia
                break
        else:
            self.gio_hang.append({'ma_sp': ma_sp, 'ten_sp': ten_sp, 'gia': gia, 'so_luong': soluong, 'thanh_tien': gia * soluong})

        self.entry_soluong.delete(0, tk.END)
        self.cap_nhat_gio_hang_gui()

    def xoa_khoi_gio_hang(self):
        selected = self.tree_gio.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món trong giỏ để xóa!")
            return
        idx = self.tree_gio.index(selected[0])
        del self.gio_hang[idx]
        self.cap_nhat_gio_hang_gui()

    def cap_nhat_gio_hang_gui(self):
        for item in self.tree_gio.get_children(): self.tree_gio.delete(item)
        tam_tinh = sum(item['thanh_tien'] for item in self.gio_hang)
        giam_gia = 0
        
        selected_voucher = self.combo_voucher.get()
        if selected_voucher and selected_voucher != "Không dùng Voucher":
            ma_vc = selected_voucher.split(" ")[0]
            conn = sqlite3.connect('hethong_banhang_v3.db')
            cursor = conn.cursor()
            cursor.execute("SELECT GiamGia, LoaiGiam FROM Voucher WHERE MaVoucher = ?", (ma_vc,))
            vc = cursor.fetchone()
            conn.close()
            if vc:
                giam_gia = tam_tinh * (vc[0] / 100.0) if vc[1] == 'PERCENT' else vc[0]

        sau_giam = max(0, tam_tinh - giam_gia)
        thue = sau_giam * self.VAT_RATE
        tong_tien = sau_giam + thue
        
        for idx, item in enumerate(self.gio_hang, 1):
            self.tree_gio.insert("", tk.END, values=(idx, item['ma_sp'], item['ten_sp'], f"{item['gia']:,.0f} VNĐ", item['so_luong'], f"{item['thanh_tien']:,.0f} VNĐ"))
            
        self.lbl_tamtinh.config(text=f"Tạm tính: {tam_tinh:,.0f} VNĐ | Giảm: {giam_gia:,.0f} VNĐ | Thuế (10%): {thue:,.0f} VNĐ | TỔNG: {tong_tien:,.0f} VNĐ")

    def tao_don_hang_cho(self):
        if not self.gio_hang:
            messagebox.showwarning("Giỏ trống", "Chưa có sản phẩm nào trong giỏ!")
            return
            
        tam_tinh = sum(item['thanh_tien'] for item in self.gio_hang)
        giam_gia = 0
        selected_vc = self.combo_voucher.get()
        ma_vc = None
        
        if selected_vc and selected_vc != "Không dùng Voucher":
            ma_vc = selected_vc.split(" ")[0]
            conn = sqlite3.connect('hethong_banhang_v3.db')
            cursor = conn.cursor()
            cursor.execute("SELECT GiamGia, LoaiGiam FROM Voucher WHERE MaVoucher = ?", (ma_vc,))
            vc = cursor.fetchone()
            conn.close()
            if vc:
                giam_gia = tam_tinh * (vc[0] / 100.0) if vc[1] == 'PERCENT' else vc[0]

        sau_giam = max(0, tam_tinh - giam_gia)
        thue = sau_giam * self.VAT_RATE
        tong_tien = sau_giam + thue
        ngay_dat = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        
        cursor.execute("""INSERT INTO DonHang (TenKH, NgayDat, TrangThai, TamTinh, GiamGia, Thue, TongTien) 
                          VALUES (?, ?, 'Chờ thanh toán', ?, ?, ?, ?)""", 
                       (self.user_name, ngay_dat, tam_tinh, giam_gia, thue, tong_tien))
        ma_dh = cursor.lastrowid
        
        for item in self.gio_hang:
            cursor.execute("INSERT INTO ChiTietDonHang VALUES (?, ?, ?)", (ma_dh, item['ma_sp'], item['so_luong']))
            cursor.execute("UPDATE SanPham SET SoLuongKho = SoLuongKho - ? WHERE MaSP = ?", (item['so_luong'], item['ma_sp']))
            
        if ma_vc:
            cursor.execute("UPDATE ViVoucher SET TrangThai = 'DA_SU_DUNG' WHERE TenKH = ? AND MaVoucher = ?", 
                           (self.user_name, ma_vc))

        conn.commit()
        conn.close()

        messagebox.showinfo("Thành công", f"🎉 Tạo đơn thành công! Mã đơn #{ma_dh}.")
        self.gio_hang = []
        self.cap_nhat_gio_hang_gui()
        self.load_san_pham_kho()
        self.load_cho_thanh_toan()
        self.load_vi_voucher_cb()

    # ------------------------------------------
    # TAB 2: CHỜ THANH TOÁN
    # ------------------------------------------
    def build_tab_thanhtoan(self):
        top = ttk.Frame(self.tab_thanhtoan)
        top.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top, text="Chọn đơn chờ thanh toán:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.combo_chothanhtoan = ttk.Combobox(top, width=35, state="readonly")
        self.combo_chothanhtoan.pack(side=tk.LEFT, padx=5)
        self.combo_chothanhtoan.bind("<<ComboboxSelected>>", lambda e: self.xem_chi_tiet_cho_thanh_toan())

        btn_xacnhan_tt = tk.Button(top, text="💳 THANH TOÁN", command=self.hoan_tat_thanh_toan,
                                   bg="#e67e22", fg="white", font=("Arial", 9, "bold"), padx=8)
        btn_xacnhan_tt.pack(side=tk.LEFT, padx=5)

        btn_xoa_dh_cho = tk.Button(top, text="🗑️ XÓA ĐƠN", command=self.xoa_don_cho_thanh_toan,
                                   bg="#e74c3c", fg="white", font=("Arial", 9, "bold"), padx=8)
        btn_xoa_dh_cho.pack(side=tk.LEFT, padx=5)

        frame_detail = ttk.LabelFrame(self.tab_thanhtoan, text=" Chi tiết đơn hàng đang chờ ")
        frame_detail.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        cols = ("STT", "Tên Sản Phẩm", "Đơn Giá", "Số Lượng", "Thành Tiền")
        self.tree_cho = ttk.Treeview(frame_detail, columns=cols, show="headings", height=6)
        for c in cols: self.tree_cho.heading(c, text=c)
        self.tree_cho.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.lbl_info_cho = tk.Label(self.tab_thanhtoan, text="Tạm tính: 0 VNĐ | Giảm: 0 VNĐ | Thuế: 0 VNĐ | TỔNG CỘNG: 0 VNĐ", 
                                     font=("Arial", 11, "bold"), fg="#c0392b")
        self.lbl_info_cho.pack(anchor=tk.E, padx=15, pady=10)

    def load_cho_thanh_toan(self):
        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        if self.user_role == "Khách hàng":
            cursor.execute("SELECT MaDH, TenKH, NgayDat, TongTien FROM DonHang WHERE TrangThai = 'Chờ thanh toán' AND TenKH = ? ORDER BY MaDH DESC", (self.user_name,))
        else:
            cursor.execute("SELECT MaDH, TenKH, NgayDat, TongTien FROM DonHang WHERE TrangThai = 'Chờ thanh toán' ORDER BY MaDH DESC")
            
        rows = cursor.fetchall()
        conn.close()
        
        vals = [f"Đơn #{r[0]} - Khách: {r[1]} ({r[2]}) - Tổng: {r[3]:,.0f} VNĐ" for r in rows]
        self.combo_chothanhtoan['values'] = vals
        
        if vals:
            self.combo_chothanhtoan.current(0)
            self.xem_chi_tiet_cho_thanh_toan()
        else:
            self.combo_chothanhtoan.set('')
            for item in self.tree_cho.get_children(): self.tree_cho.delete(item)
            self.lbl_info_cho.config(text="Không có đơn hàng nào chờ thanh toán.")

    def xem_chi_tiet_cho_thanh_toan(self):
        val = self.combo_chothanhtoan.get()
        ma_dh = self.Lay_Ma_Don_Hang(val)
        if not ma_dh:
            for item in self.tree_cho.get_children(): self.tree_cho.delete(item)
            self.lbl_info_cho.config(text="Không có đơn hàng nào được chọn.")
            return

        for item in self.tree_cho.get_children(): self.tree_cho.delete(item)
        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT TamTinh, GiamGia, Thue, TongTien FROM DonHang WHERE MaDH = ?", (ma_dh,))
        dh = cursor.fetchone()
        if not dh:
            conn.close()
            return
            
        cursor.execute("""SELECT sp.TenSP, sp.Gia, ct.SoLuong, (sp.Gia * ct.SoLuong) 
                          FROM ChiTietDonHang ct JOIN SanPham sp ON ct.MaSP = sp.MaSP WHERE ct.MaDH = ?""", (ma_dh,))
        rows = cursor.fetchall()
        conn.close()
        
        for idx, r in enumerate(rows, 1):
            self.tree_cho.insert("", tk.END, values=(idx, r[0], f"{r[1]:,.0f} VNĐ", r[2], f"{r[3]:,.0f} VNĐ"))
            
        self.lbl_info_cho.config(text=f"Tạm tính: {dh[0]:,.0f} VNĐ | Giảm giá: {dh[1]:,.0f} VNĐ | Thuế (10%): {dh[2]:,.0f} VNĐ | TỔNG CỘNG THANH TOÁN: {dh[3]:,.0f} VNĐ")

    def hoan_tat_thanh_toan(self):
        val = self.combo_chothanhtoan.get()
        ma_dh = self.Lay_Ma_Don_Hang(val)
        if not ma_dh:
            messagebox.showwarning("Cảnh báo", "Không có đơn hàng nào được chọn!")
            return
            
        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE DonHang SET TrangThai = 'Đã thanh toán' WHERE MaDH = ?", (ma_dh,))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Thành công", f"✅ Đơn hàng #{ma_dh} đã thanh toán thành công!")
        self.load_cho_thanh_toan()
        self.load_danh_sach_lich_su()

    def xoa_don_cho_thanh_toan(self):
        val = self.combo_chothanhtoan.get()
        ma_dh = self.Lay_Ma_Don_Hang(val)
        if not ma_dh:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đơn hàng cần xóa!")
            return

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa đơn hàng chờ #{ma_dh} này không? (Số lượng kho sẽ được hoàn trả)"):
            return

        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT MaSP, SoLuong FROM ChiTietDonHang WHERE MaDH = ?", (ma_dh,))
        items = cursor.fetchall()
        for item in items:
            cursor.execute("UPDATE SanPham SET SoLuongKho = SoLuongKho + ? WHERE MaSP = ?", (item[1], item[0]))

        cursor.execute("DELETE FROM ChiTietDonHang WHERE MaDH = ?", (ma_dh,))
        cursor.execute("DELETE FROM DonHang WHERE MaDH = ?", (ma_dh,))
        
        conn.commit()
        conn.close()

        messagebox.showinfo("Thành công", f"🗑️ Đã xóa đơn hàng chờ #{ma_dh} thành công!")
        self.load_cho_thanh_toan()
        self.load_san_pham_kho()

    # ------------------------------------------
    # TAB 3: LỊCH SỬ ĐƠN HÀNG
    # ------------------------------------------
    def build_tab_lichsu(self):
        top = ttk.Frame(self.tab_lichsu)
        top.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top, text="Chọn đơn hàng đã hoàn thành:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.combo_lichsu = ttk.Combobox(top, width=40, state="readonly")
        self.combo_lichsu.pack(side=tk.LEFT, padx=5)
        self.combo_lichsu.bind("<<ComboboxSelected>>", lambda e: self.xem_chi_tiet_lich_su())
        
        btn_xoa_ls = tk.Button(top, text="🗑️ XÓA DỮ LIỆU ĐƠN", command=self.xoa_lich_su_don_hang,
                               bg="#c0392b", fg="white", font=("Arial", 9, "bold"), padx=8)
        btn_xoa_ls.pack(side=tk.LEFT, padx=10)

        frame_detail = ttk.LabelFrame(self.tab_lichsu, text=" Chi tiết hóa đơn ")
        frame_detail.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        cols = ("STT", "Tên Sản Phẩm", "Đơn Giá", "Số Lượng", "Thành Tiền")
        self.tree_ls = ttk.Treeview(frame_detail, columns=cols, show="headings", height=6)
        for c in cols: self.tree_ls.heading(c, text=c)
        self.tree_ls.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.lbl_info_ls = tk.Label(self.tab_lichsu, text="TỔNG TIỀN ĐÃ THANH TOÁN: 0 VNĐ", font=("Arial", 13, "bold"), fg="#27ae60")
        self.lbl_info_ls.pack(anchor=tk.E, padx=15, pady=10)

    def load_danh_sach_lich_su(self):
        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        if self.user_role == "Khách hàng":
            cursor.execute("SELECT MaDH, TenKH, NgayDat FROM DonHang WHERE TrangThai = 'Đã thanh toán' AND TenKH = ? ORDER BY MaDH DESC", (self.user_name,))
        else:
            cursor.execute("SELECT MaDH, TenKH, NgayDat FROM DonHang WHERE TrangThai = 'Đã thanh toán' ORDER BY MaDH DESC")
            
        rows = cursor.fetchall()
        conn.close()
        
        vals = [f"Đơn #{r[0]} - Khách: {r[1]} ({r[2]})" for r in rows]
        self.combo_lichsu['values'] = vals
        
        if vals:
            self.combo_lichsu.current(0)
            self.xem_chi_tiet_lich_su()
        else:
            self.combo_lichsu.set('')
            for item in self.tree_ls.get_children(): self.tree_ls.delete(item)
            self.lbl_info_ls.config(text="Chưa có lịch sử đơn hàng.")

    def xem_chi_tiet_lich_su(self):
        val = self.combo_lichsu.get()
        ma_dh = self.Lay_Ma_Don_Hang(val)
        if not ma_dh:
            for item in self.tree_ls.get_children(): self.tree_ls.delete(item)
            self.lbl_info_ls.config(text="Không có đơn hàng được chọn.")
            return

        for item in self.tree_ls.get_children(): self.tree_ls.delete(item)
        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT TongTien FROM DonHang WHERE MaDH = ?", (ma_dh,))
        dh = cursor.fetchone()
        if not dh:
            conn.close()
            return
            
        tong = dh[0]
        cursor.execute("""SELECT sp.TenSP, sp.Gia, ct.SoLuong, (sp.Gia * ct.SoLuong) 
                          FROM ChiTietDonHang ct JOIN SanPham sp ON ct.MaSP = sp.MaSP WHERE ct.MaDH = ?""", (ma_dh,))
        rows = cursor.fetchall()
        conn.close()
        
        for idx, r in enumerate(rows, 1):
            self.tree_ls.insert("", tk.END, values=(idx, r[0], f"{r[1]:,.0f} VNĐ", r[2], f"{r[3]:,.0f} VNĐ"))
        self.lbl_info_ls.config(text=f"TỔNG CỘNG ĐÃ THANH TOÁN: {tong:,.0f} VNĐ")

    def xoa_lich_su_don_hang(self):
        val = self.combo_lichsu.get()
        ma_dh = self.Lay_Ma_Don_Hang(val)
        if not ma_dh:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đơn hàng lịch sử cần xóa!")
            return

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa vĩnh viễn dữ liệu đơn hàng #{ma_dh} này khỏi lịch sử không?"):
            return

        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ChiTietDonHang WHERE MaDH = ?", (ma_dh,))
        cursor.execute("DELETE FROM DonHang WHERE MaDH = ?", (ma_dh,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Thành công", f"🗑️ Đã xóa dữ liệu đơn hàng #{ma_dh} khỏi lịch sử!")
        self.load_danh_sach_lich_su()

    # ------------------------------------------
    # TAB 4: QUẢN LÝ DÀNH CHO NHÂN VIÊN (ĐÃ THÊM NÚT XÓA SP & VOUCHER)
    # ------------------------------------------
    def build_tab_quanly_nv(self):
        nb_nv = ttk.Notebook(self.tab_quanly)
        nb_nv.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tab_sp = ttk.Frame(nb_nv)
        tab_vc = ttk.Frame(nb_nv)
        
        nb_nv.add(tab_sp, text=" 📦 QUẢN LÝ SẢN PHẨM ")
        nb_nv.add(tab_vc, text=" 🎟️ QUẢN LÝ VOUCHER ")
        
        # --- SUB TAB 1: SẢN PHẨM ---
        frame_list_sp = ttk.LabelFrame(tab_sp, text=" Danh Sách Sản Phẩm ")
        frame_list_sp.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        cols_sp = ("Mã SP", "Tên Sản Phẩm", "Đơn Giá", "Tồn Kho")
        self.tree_qlkho = ttk.Treeview(frame_list_sp, columns=cols_sp, show="headings", height=6)
        for c in cols_sp: self.tree_qlkho.heading(c, text=c)
        self.tree_qlkho.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree_qlkho.bind("<<TreeviewSelect>>", self.hien_thi_thong_tin_sua)
        
        frame_form_sp = ttk.LabelFrame(tab_sp, text=" Thêm / Cập Nhật / Xóa Sản Phẩm ")
        frame_form_sp.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(frame_form_sp, text="Mã SP:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_masp_form = ttk.Entry(frame_form_sp, width=12)
        self.entry_masp_form.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form_sp, text="Tên Sản Phẩm:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_tensp_form = ttk.Entry(frame_form_sp, width=25)
        self.entry_tensp_form.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_form_sp, text="Đơn giá (VNĐ):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_gia_form = ttk.Entry(frame_form_sp, width=12)
        self.entry_gia_form.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form_sp, text="Tồn kho:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_kho_form = ttk.Entry(frame_form_sp, width=12)
        self.entry_kho_form.grid(row=1, column=3, padx=5, pady=5)
        
        btn_them_sp = tk.Button(frame_form_sp, text="➕ THÊM MỚI", command=self.them_san_pham_gui, bg="#2980b9", fg="white", font=("Arial", 9, "bold"), width=15)
        btn_them_sp.grid(row=0, column=4, padx=10, pady=2)
        
        btn_capnhat_sp = tk.Button(frame_form_sp, text="💾 CẬP NHẬT", command=self.cap_nhat_san_pham_gui, bg="#27ae60", fg="white", font=("Arial", 9, "bold"), width=15)
        btn_capnhat_sp.grid(row=1, column=4, padx=10, pady=2)

        # ➕ NÚT XÓA SẢN PHẨM MỚI THÊM
        btn_xoa_sp = tk.Button(frame_form_sp, text="🗑️ XÓA SP", command=self.xoa_san_pham_gui, bg="#c0392b", fg="white", font=("Arial", 9, "bold"), width=15)
        btn_xoa_sp.grid(row=2, column=4, padx=10, pady=2)

        self.load_danh_sach_qlkho()

        # --- SUB TAB 2: VOUCHER ---
        frame_list_vc = ttk.LabelFrame(tab_vc, text=" Danh Sách Voucher Hiện Tại ")
        frame_list_vc.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        cols_vc = ("Mã Voucher", "Mô Tả", "Loại Giảm", "Giá Trị", "Số Lượng")
        self.tree_nv_vc = ttk.Treeview(frame_list_vc, columns=cols_vc, show="headings", height=6)
        for c in cols_vc: self.tree_nv_vc.heading(c, text=c)
        self.tree_nv_vc.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        frame_form_vc = ttk.LabelFrame(tab_vc, text=" Tạo Mới / Xóa Voucher ")
        frame_form_vc.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(frame_form_vc, text="Mã Voucher:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_mavc_new = ttk.Entry(frame_form_vc, width=15)
        self.entry_mavc_new.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form_vc, text="Mô tả ngắn:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_motavc_new = ttk.Entry(frame_form_vc, width=30)
        self.entry_motavc_new.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_form_vc, text="Loại giảm:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_loaivc_new = ttk.Combobox(frame_form_vc, values=["Theo % (PERCENT)", "Số tiền cố định (AMOUNT)"], state="readonly", width=22)
        self.combo_loaivc_new.current(0)
        self.combo_loaivc_new.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form_vc, text="Giá trị giảm:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_gtvc_new = ttk.Entry(frame_form_vc, width=15)
        self.entry_gtvc_new.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(frame_form_vc, text="Số lượng phát hành:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_slvc_new = ttk.Entry(frame_form_vc, width=15)
        self.entry_slvc_new.grid(row=2, column=1, padx=5, pady=5)

        btn_taovc = tk.Button(frame_form_vc, text="🎟️ TẠO VOUCHER", command=self.tao_voucher_gui, bg="#8e44ad", fg="white", font=("Arial", 9, "bold"), width=15, pady=2)
        btn_taovc.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        # ➕ NÚT XÓA VOUCHER MỚI THÊM
        btn_xoavc = tk.Button(frame_form_vc, text="🗑️ XÓA VOUCHER", command=self.xoa_voucher_gui, bg="#c0392b", fg="white", font=("Arial", 9, "bold"), width=15, pady=2)
        btn_xoavc.grid(row=2, column=3, sticky="e", padx=5, pady=5)

        self.load_nv_danh_sach_voucher()

    def load_danh_sach_qlkho(self):
        for item in self.tree_qlkho.get_children(): self.tree_qlkho.delete(item)
        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MaSP, TenSP, Gia, SoLuongKho FROM SanPham")
        for r in cursor.fetchall():
            self.tree_qlkho.insert("", tk.END, values=(r[0], r[1], f"{r[2]:,.0f}", r[3]))
        conn.close()

    def hien_thi_thong_tin_sua(self, event):
        selected = self.tree_qlkho.selection()
        if not selected: return
        vals = self.tree_qlkho.item(selected[0], 'values')
        
        self.entry_masp_form.delete(0, tk.END)
        self.entry_masp_form.insert(0, vals[0])
        self.entry_tensp_form.delete(0, tk.END)
        self.entry_tensp_form.insert(0, vals[1])
        self.entry_gia_form.delete(0, tk.END)
        self.entry_gia_form.insert(0, vals[2].replace(",", ""))
        self.entry_kho_form.delete(0, tk.END)
        self.entry_kho_form.insert(0, vals[3])

    def them_san_pham_gui(self):
        try:
            ma_sp = int(self.entry_masp_form.get().strip())
            ten_sp = self.entry_tensp_form.get().strip()
            gia = float(self.entry_gia_form.get().strip())
            kho = int(self.entry_kho_form.get().strip())
            if not ten_sp or gia < 0 or kho < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin sản phẩm hợp lệ!")
            return

        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO SanPham VALUES (?, ?, ?, ?)", (ma_sp, ten_sp, gia, kho))
            conn.commit()
            messagebox.showinfo("Thành công", f"✅ Thêm thành công sản phẩm: {ten_sp}")
            self.load_danh_sach_qlkho()
            self.load_san_pham_kho()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", f"Mã sản phẩm {ma_sp} đã tồn tại!")
        finally:
            conn.close()

    def cap_nhat_san_pham_gui(self):
        ma_sp = self.entry_masp_form.get().strip()
        if not ma_sp:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn 1 sản phẩm để cập nhật!")
            return
            
        try:
            gia_moi = float(self.entry_gia_form.get().strip())
            kho_moi = int(self.entry_kho_form.get().strip())
            if gia_moi < 0 or kho_moi < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Giá bán và Số lượng kho phải là số không âm!")
            return

        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE SanPham SET Gia = ?, SoLuongKho = ? WHERE MaSP = ?", (gia_moi, kho_moi, ma_sp))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Thành công", f"✅ Cập nhật sản phẩm #{ma_sp} thành công!")
        self.load_danh_sach_qlkho()
        self.load_san_pham_kho()

    def xoa_san_pham_gui(self):
        """Hàm xử lý xóa sản phẩm dựa vào Mã SP đang điền hoặc chọn"""
        ma_sp = self.entry_masp_form.get().strip()
        if not ma_sp:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hoặc nhập Mã sản phẩm cần xóa!")
            return

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa sản phẩm mã #{ma_sp} này không?"):
            return

        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM SanPham WHERE MaSP = ?", (ma_sp,))
            conn.commit()
            messagebox.showinfo("Thành công", f"🗑️ Đã xóa sản phẩm #{ma_sp} thành công!")
            self.load_danh_sach_qlkho()
            self.load_san_pham_kho()
            
            # Làm trống khung nhập
            self.entry_masp_form.delete(0, tk.END)
            self.entry_tensp_form.delete(0, tk.END)
            self.entry_gia_form.delete(0, tk.END)
            self.entry_kho_form.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Không thể xóa sản phẩm này vì đã phát sinh lịch sử đơn hàng liên quan!")
        finally:
            conn.close()

    def load_nv_danh_sach_voucher(self):
        for item in self.tree_nv_vc.get_children(): self.tree_nv_vc.delete(item)
        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MaVoucher, MoTa, LoaiGiam, GiamGia, SoLuong FROM Voucher")
        for r in cursor.fetchall():
            loai = "%" if r[2] == 'PERCENT' else "VNĐ"
            gt = f"{r[3]:,.0f} {loai}"
            self.tree_nv_vc.insert("", tk.END, values=(r[0], r[1], r[2], gt, r[4]))
        conn.close()

    def tao_voucher_gui(self):
        ma_vc = self.entry_mavc_new.get().strip().upper()
        mo_ta = self.entry_motavc_new.get().strip()
        loai_sel = self.combo_loaivc_new.get()
        loai_giam = "PERCENT" if "PERCENT" in loai_sel else "AMOUNT"

        try:
            giam_gia = float(self.entry_gtvc_new.get().strip())
            so_luong = int(self.entry_slvc_new.get().strip())
            if not ma_vc or not mo_ta or giam_gia <= 0 or so_luong <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ và chính xác thông tin Voucher!")
            return

        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Voucher VALUES (?, ?, ?, ?, ?)", (ma_vc, mo_ta, giam_gia, loai_giam, so_luong))
            conn.commit()
            messagebox.showinfo("Thành công", f"🎉 Đã tạo mới Voucher [{ma_vc}] thành công!")
            self.load_nv_danh_sach_voucher()
            if hasattr(self, 'tree_vouchers'):
                self.load_danh_sach_voucher()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", f"Mã Voucher [{ma_vc}] đã tồn tại!")
        finally:
            conn.close()

    def xoa_voucher_gui(self):
        """Hàm xử lý xóa Voucher được chọn từ bảng danh sách voucher"""
        selected = self.tree_nv_vc.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn 1 Voucher trong danh sách ở trên để xóa!")
            return
            
        vals = self.tree_nv_vc.item(selected[0], 'values')
        ma_vc = vals[0]

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa vĩnh viễn Voucher [{ma_vc}] không?"):
            return

        conn = sqlite3.connect('hethong_banhang_v3.db')
        cursor = conn.cursor()
        try:
            # Xóa cả trong ví voucher của khách để tránh lỗi liên kết
            cursor.execute("DELETE FROM ViVoucher WHERE MaVoucher = ?", (ma_vc,))
            cursor.execute("DELETE FROM Voucher WHERE MaVoucher = ?", (ma_vc,))
            conn.commit()
            messagebox.showinfo("Thành công", f"🗑️ Đã xóa Voucher [{ma_vc}] thành công!")
            self.load_nv_danh_sach_voucher()
            if hasattr(self, 'tree_vouchers'):
                self.load_danh_sach_voucher()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa voucher: {e}")
        finally:
            conn.close()

# ==========================================
# 5. CHẠY CHƯƠNG TRÌNH
# ==========================================
if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()