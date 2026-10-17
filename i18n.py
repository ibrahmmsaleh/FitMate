"""Terjemahan Indonesia (id) dan Inggris (en).

Setiap kunci punya pasangan (teks_id, teks_en) berdampingan, jadi mudah
memeriksa bahwa kedua bahasa selalu lengkap. Pakai di template: {{ t('kunci') }}.
Teks boleh berisi {placeholder}, diisi lewat t('kunci', nama=nilai).
"""

LANGUAGES = ("id", "en")
DEFAULT_LANGUAGE = "id"

S = {
    # ---- Umum ----
    "app.tagline": ("Asisten latihan pribadi", "Your personal training assistant"),
    "nav.home": ("Beranda", "Home"),
    "nav.dashboard": ("Dashboard", "Dashboard"),
    "nav.program": ("Program", "Program"),
    "nav.exercises": ("Latihan", "Exercises"),
    "nav.log": ("Catat", "Log"),
    "nav.progress": ("Progres", "Progress"),
    "nav.profile": ("Profil", "Profile"),
    "nav.login": ("Masuk", "Log in"),
    "nav.register": ("Daftar", "Sign up"),
    "nav.logout": ("Keluar", "Log out"),
    "nav.skip": ("Lewati ke konten", "Skip to content"),
    "nav.language": ("Bahasa", "Language"),
    "disclaimer": (
        "FitMate memberi saran umum, bukan nasihat medis. Konsultasikan ke dokter sebelum memulai program latihan, "
        "terutama bila Anda punya kondisi kesehatan atau cedera.",
        "FitMate gives general guidance, not medical advice. Talk to a doctor before starting a training program, "
        "especially if you have a health condition or injury.",
    ),
    "storage.notice": (
        "Mode demo: data disimpan sementara di server dan bisa hilang sewaktu-waktu.",
        "Demo mode: data is stored temporarily on the server and may disappear at any time.",
    ),
    "today": ("Hari ini", "Today"),
    "save": ("Simpan", "Save"),
    "cancel": ("Batal", "Cancel"),
    "edit": ("Ubah", "Edit"),
    "delete": ("Hapus", "Delete"),
    "add": ("Tambah", "Add"),
    "apply": ("Terapkan", "Apply"),
    "reset": ("Atur ulang", "Reset"),
    "all": ("Semua", "All"),
    "confirm.delete": ("Hapus data ini?", "Delete this entry?"),
    "unit.kg": ("kg", "kg"),
    "unit.min": ("menit", "min"),
    "unit.sec": ("dtk", "sec"),
    "week.aria": ("Jadwal latihan satu minggu", "One-week training schedule"),

    # ---- Hari, sesi, enum ----
    "weekday.0": ("Senin", "Monday"), "weekday.1": ("Selasa", "Tuesday"), "weekday.2": ("Rabu", "Wednesday"),
    "weekday.3": ("Kamis", "Thursday"), "weekday.4": ("Jumat", "Friday"), "weekday.5": ("Sabtu", "Saturday"),
    "weekday.6": ("Minggu", "Sunday"),
    "weekday.short.0": ("Sen", "Mon"), "weekday.short.1": ("Sel", "Tue"), "weekday.short.2": ("Rab", "Wed"),
    "weekday.short.3": ("Kam", "Thu"), "weekday.short.4": ("Jum", "Fri"), "weekday.short.5": ("Sab", "Sat"),
    "weekday.short.6": ("Min", "Sun"),
    "month.1": ("Jan", "Jan"), "month.2": ("Feb", "Feb"), "month.3": ("Mar", "Mar"), "month.4": ("Apr", "Apr"),
    "month.5": ("Mei", "May"), "month.6": ("Jun", "Jun"), "month.7": ("Jul", "Jul"), "month.8": ("Agu", "Aug"),
    "month.9": ("Sep", "Sep"), "month.10": ("Okt", "Oct"), "month.11": ("Nov", "Nov"), "month.12": ("Des", "Dec"),
    "session.full": ("Seluruh tubuh", "Full body"),
    "session.upper": ("Tubuh atas", "Upper body"),
    "session.lower": ("Tubuh bawah", "Lower body"),
    "session.push": ("Dorong", "Push"),
    "session.pull": ("Tarik", "Pull"),
    "session.legs": ("Kaki", "Legs"),
    "session.rest": ("Istirahat", "Rest"),
    "goal.lose_fat": ("Menurunkan berat badan", "Lose weight"),
    "goal.muscle": ("Menambah massa otot", "Build muscle"),
    "goal.strength": ("Menambah kekuatan", "Get stronger"),
    "goal.fitness": ("Kebugaran umum", "General fitness"),
    "level.beginner": ("Pemula", "Beginner"),
    "level.intermediate": ("Menengah", "Intermediate"),
    "level.advanced": ("Lanjut", "Advanced"),
    "equip.bodyweight": ("Tanpa alat", "No equipment"),
    "equip.dumbbell": ("Dumbbell di rumah", "Dumbbells at home"),
    "equip.gym": ("Gym lengkap", "Full gym"),
    "muscle.chest": ("Dada", "Chest"),
    "muscle.shoulders": ("Bahu", "Shoulders"),
    "muscle.triceps": ("Trisep", "Triceps"),
    "muscle.back": ("Punggung", "Back"),
    "muscle.biceps": ("Bisep", "Biceps"),
    "muscle.quads": ("Paha depan", "Quads"),
    "muscle.hamstrings": ("Paha belakang", "Hamstrings"),
    "muscle.glutes": ("Bokong", "Glutes"),
    "muscle.calves": ("Betis", "Calves"),
    "muscle.core": ("Perut dan core", "Core"),
    "kind.compound": ("Gerakan majemuk", "Compound movement"),
    "kind.isolation": ("Gerakan isolasi", "Isolation movement"),

    # ---- Beranda ----
    "home.title": ("Latihan yang jelas, setiap minggu.", "A clear plan for every training week."),
    "home.lead": (
        "FitMate menyusun jadwal latihan sesuai tujuan, alat, dan waktu Anda, lalu membantu Anda mencatat sesi "
        "dan melihat kemajuannya.",
        "FitMate builds a weekly schedule around your goal, equipment, and time, then helps you log sessions "
        "and watch your progress.",
    ),
    "home.cta.register": ("Buat akun gratis", "Create a free account"),
    "home.cta.dashboard": ("Buka dashboard", "Open dashboard"),
    "home.sample.title": ("Contoh minggu latihan", "Sample training week"),
    "home.sample.note": (
        "Contoh nyata dari mesin rekomendasi: pemula, 3 hari per minggu, tanpa alat.",
        "A real output of the recommender: beginner, 3 days a week, no equipment.",
    ),
    "home.steps.title": ("Cara kerjanya", "How it works"),
    "home.step1.title": ("Isi profil", "Fill in your profile"),
    "home.step1.text": ("Tujuan, level, alat, dan jumlah hari latihan.", "Goal, level, equipment, and training days."),
    "home.step2.title": ("Dapatkan program", "Get your program"),
    "home.step2.text": (
        "Jadwal mingguan lengkap dengan set, repetisi, dan waktu istirahat.",
        "A weekly schedule with sets, reps, and rest times.",
    ),
    "home.step3.title": ("Catat dan pantau", "Log and track"),
    "home.step3.text": (
        "Catat tiap sesi dan berat badan, lalu lihat grafiknya.",
        "Log each session and your body weight, then see the charts.",
    ),
    "home.note": (
        "Rekomendasi dibuat dengan aturan umum, bukan oleh AI atau pelatih sungguhan.",
        "Recommendations come from general rules, not from AI or a human coach.",
    ),

    # ---- Akun ----
    "auth.register.title": ("Buat akun", "Create account"),
    "auth.register.submit": ("Daftar", "Sign up"),
    "auth.login.title": ("Masuk", "Log in"),
    "auth.login.submit": ("Masuk", "Log in"),
    "auth.name": ("Nama", "Name"),
    "auth.email": ("Email", "Email"),
    "auth.password": ("Kata sandi", "Password"),
    "auth.password2": ("Ulangi kata sandi", "Repeat password"),
    "auth.password_hint": ("Minimal 8 karakter.", "At least 8 characters."),
    "auth.have_account": ("Sudah punya akun?", "Already have an account?"),
    "auth.no_account": ("Belum punya akun?", "No account yet?"),

    # ---- Pesan ----
    "flash.registered": (
        "Akun dibuat. Lengkapi profil Anda untuk mendapat program.",
        "Account created. Complete your profile to get a program.",
    ),
    "flash.login_failed": ("Email atau kata sandi salah.", "Incorrect email or password."),
    "flash.logged_out": ("Anda sudah keluar.", "You have logged out."),
    "flash.need_login": ("Masuk dulu untuk membuka halaman itu.", "Log in to open that page."),
    "flash.need_profile": (
        "Isi profil dulu agar program bisa disusun.",
        "Fill in your profile first so we can build your program.",
    ),
    "flash.session_lost": ("Sesi Anda berakhir. Masuk kembali.", "Your session ended. Please log in again."),
    "flash.profile_saved": (
        "Profil disimpan. Program Anda sudah diperbarui.",
        "Profile saved. Your program has been updated.",
    ),
    "flash.log_saved": ("Catatan latihan disimpan.", "Workout saved."),
    "flash.log_updated": ("Catatan latihan diperbarui.", "Workout updated."),
    "flash.log_deleted": ("Catatan latihan dihapus.", "Workout deleted."),
    "flash.weight_saved": ("Berat badan dicatat.", "Body weight logged."),
    "flash.weight_deleted": ("Catatan berat badan dihapus.", "Weight entry deleted."),
    "flash.account_deleted": (
        "Akun dan semua datanya sudah dihapus.",
        "Your account and all its data were deleted.",
    ),
    "flash.form_errors": ("Periksa kembali isian yang bertanda.", "Please check the highlighted fields."),
    "err.name": ("Isi nama (maksimal 60 karakter).", "Enter a name (60 characters max)."),
    "err.email": ("Masukkan email yang valid.", "Enter a valid email address."),
    "err.email_taken": ("Email itu sudah terdaftar.", "That email is already registered."),
    "err.password_length": ("Kata sandi harus 8–128 karakter.", "Password must be 8–128 characters."),
    "err.password_match": ("Kata sandi tidak sama.", "Passwords do not match."),
    "err.age": ("Usia harus 15–80 tahun.", "Age must be between 15 and 80."),
    "err.height_cm": ("Tinggi harus 120–230 cm.", "Height must be 120–230 cm."),
    "err.weight_kg": ("Berat harus 30–250 kg.", "Weight must be 30–250 kg."),
    "err.days": ("Pilih 2–6 hari.", "Choose 2–6 days."),
    "err.choice": ("Pilih salah satu opsi.", "Choose one option."),
    "err.date": ("Tanggal tidak valid atau di masa depan.", "Invalid date, or a date in the future."),
    "err.sets": ("Set harus 1–20.", "Sets must be 1–20."),
    "err.reps": ("Repetisi atau detik harus 1–600.", "Reps or seconds must be 1–600."),
    "err.weight_load": ("Beban harus 0–500 kg.", "Weight must be 0–500 kg."),
    "err.note": ("Catatan maksimal 200 karakter.", "Note must be 200 characters or fewer."),
    "err.404.title": ("Halaman tidak ditemukan", "Page not found"),
    "err.404.text": ("Alamat yang Anda buka tidak ada.", "That address does not exist."),
    "err.400.title": ("Formulir kedaluwarsa", "Form expired"),
    "err.400.text": (
        "Muat ulang halaman, lalu kirim formulir sekali lagi.",
        "Reload the page, then submit the form again.",
    ),
    "err.back_home": ("Kembali ke beranda", "Back to home"),

    # ---- Profil ----
    "profile.title": ("Profil kebugaran", "Fitness profile"),
    "profile.lead": (
        "Data ini hanya dipakai untuk menyusun program Anda.",
        "This data is only used to build your program.",
    ),
    "profile.age": ("Usia", "Age"),
    "profile.height": ("Tinggi badan (cm)", "Height (cm)"),
    "profile.weight": ("Berat badan sekarang (kg)", "Current weight (kg)"),
    "profile.goal": ("Tujuan", "Goal"),
    "profile.level": ("Level latihan", "Training level"),
    "profile.level_hint": (
        "Pilih Pemula bila Anda baru mulai atau sudah lama tidak berolahraga.",
        "Choose Beginner if you are just starting or have not trained for a while.",
    ),
    "profile.equipment": ("Alat yang tersedia", "Available equipment"),
    "profile.days": ("Hari latihan per minggu", "Training days per week"),
    "profile.minutes": ("Durasi tiap sesi", "Session length"),
    "profile.has_condition": (
        "Saya punya kondisi medis atau cedera yang mungkin memengaruhi latihan",
        "I have a medical condition or injury that may affect training",
    ),
    "profile.save": ("Simpan profil", "Save profile"),
    "profile.danger.title": ("Hapus akun", "Delete account"),
    "profile.danger.text": (
        "Menghapus akun akan menghapus profil, catatan latihan, dan catatan berat badan secara permanen.",
        "Deleting your account permanently removes your profile, workout logs, and weight logs.",
    ),
    "profile.danger.button": ("Hapus akun saya", "Delete my account"),
    "profile.danger.confirm": (
        "Hapus akun dan semua data? Ini tidak bisa dibatalkan.",
        "Delete your account and all data? This cannot be undone.",
    ),

    # ---- Dashboard ----
    "dash.hello": ("Halo, {name}", "Hi, {name}"),
    "dash.today": ("Sesi hari ini", "Today's session"),
    "dash.rest_today": (
        "Hari ini jadwal istirahat. Pulihkan tenaga, tidur cukup, dan jalan santai boleh.",
        "Today is a rest day. Recover, sleep well, and an easy walk is fine.",
    ),
    "dash.exercises_count": ("{n} latihan, sekitar {min} menit", "{n} exercises, about {min} min"),
    "dash.start": ("Catat latihan", "Log a workout"),
    "dash.view_program": ("Lihat program", "View program"),
    "dash.week": ("Minggu ini", "This week"),
    "dash.week_progress": ("{done} dari {planned} sesi tercatat", "{done} of {planned} sessions logged"),
    "dash.weight": ("Berat badan", "Body weight"),
    "dash.weight_none": ("Belum ada catatan berat.", "No weight entries yet."),
    "dash.weight_change": ("{delta} kg sejak {date}", "{delta} kg since {date}"),
    "dash.weight_add": ("Catat berat", "Log weight"),
    "dash.last": ("Latihan terakhir", "Last workout"),
    "dash.last_none": ("Belum ada latihan tercatat.", "No workouts logged yet."),

    # ---- Program ----
    "program.title": ("Program mingguan", "Weekly program"),
    "program.lead": (
        "Disusun untuk {days} hari per minggu. Tujuan: {goal}. Level: {level}.",
        "Built for {days} days a week. Goal: {goal}. Level: {level}.",
    ),
    "program.warmup": (
        "Pemanasan 5–10 menit sebelum mulai (jalan cepat, putar sendi), lalu peregangan ringan sesudahnya.",
        "Warm up for 5–10 minutes before starting (brisk walk, joint circles), then stretch lightly afterwards.",
    ),
    "program.progression": (
        "Bila semua set mencapai batas atas repetisi dengan teknik baik, naikkan beban sedikit pada sesi berikutnya.",
        "When every set reaches the top of the rep range with good form, add a little weight next session.",
    ),
    "program.condition_warning": (
        "Anda menandai adanya kondisi medis atau cedera. Periksakan program ini ke dokter sebelum memulai. "
        "FitMate tidak menyesuaikan program untuk kondisi tersebut.",
        "You marked a medical condition or injury. Check this program with a doctor before starting. "
        "FitMate does not adapt programs for such conditions.",
    ),
    "program.rest_text": (
        "Tidak ada sesi. Pemulihan sama pentingnya dengan latihan.",
        "No session. Recovery matters as much as training.",
    ),
    "program.few": (
        "Dengan alat dan level ini, pustaka hanya punya {n} pilihan untuk sesi ini.",
        "With this equipment and level the library only has {n} options for this session.",
    ),
    "program.col.exercise": ("Latihan", "Exercise"),
    "program.col.sets": ("Set", "Sets"),
    "program.col.reps": ("Repetisi", "Reps"),
    "program.col.rest": ("Istirahat", "Rest"),
    "program.log": ("Catat", "Log"),

    # ---- Pustaka latihan ----
    "ex.title": ("Pustaka latihan", "Exercise library"),
    "ex.search": ("Cari nama", "Search by name"),
    "ex.muscle": ("Otot", "Muscle"),
    "ex.equipment": ("Alat", "Equipment"),
    "ex.level": ("Level", "Level"),
    "ex.count": ("{n} latihan", "{n} exercises"),
    "ex.none": ("Tidak ada latihan yang cocok dengan filter ini.", "No exercises match these filters."),
    "ex.how": ("Cara melakukan", "How to do it"),
    "ex.log": ("Catat latihan ini", "Log this exercise"),
    "ex.history": ("Riwayat Anda", "Your history"),
    "ex.history_none": ("Belum pernah dicatat.", "Not logged yet."),
    "ex.best": ("Beban terbaik: {w} kg", "Best weight: {w} kg"),
    "ex.timed": (
        "Latihan tahan: isi detik pada kolom repetisi.",
        "Timed hold: enter seconds in the reps field.",
    ),
    "ex.back": ("Kembali ke pustaka", "Back to library"),

    # ---- Catat latihan ----
    "log.title": ("Catat latihan", "Log a workout"),
    "log.edit_title": ("Ubah catatan", "Edit entry"),
    "log.date": ("Tanggal", "Date"),
    "log.exercise": ("Latihan", "Exercise"),
    "log.choose": ("Pilih latihan", "Choose an exercise"),
    "log.sets": ("Set", "Sets"),
    "log.reps": ("Repetisi / detik", "Reps / seconds"),
    "log.weight": ("Beban (kg)", "Weight (kg)"),
    "log.weight_hint": ("Isi 0 untuk latihan tanpa beban.", "Enter 0 for bodyweight exercises."),
    "log.note": ("Catatan (opsional)", "Note (optional)"),
    "log.submit": ("Simpan catatan", "Save entry"),
    "log.history": ("Riwayat", "History"),
    "log.history_limit": ("Menampilkan 50 catatan terbaru.", "Showing the 50 most recent entries."),
    "log.none": (
        "Belum ada catatan. Isi formulir di atas untuk mencatat sesi pertama Anda.",
        "Nothing logged yet. Use the form above to log your first session.",
    ),
    "log.col.date": ("Tanggal", "Date"),
    "log.col.exercise": ("Latihan", "Exercise"),
    "log.col.result": ("Hasil", "Result"),
    "log.col.actions": ("Aksi", "Actions"),

    # ---- Progres ----
    "progress.title": ("Progres", "Progress"),
    "progress.weight": ("Berat badan", "Body weight"),
    "progress.weight_aria": ("Grafik berat badan dari waktu ke waktu", "Body weight over time"),
    "progress.weight_empty": ("Catat berat badan untuk melihat grafik.", "Log your weight to see the chart."),
    "progress.weight_add": ("Catat berat badan", "Log body weight"),
    "progress.weight_date": ("Tanggal", "Date"),
    "progress.weight_label": ("Berat badan (kg)", "Body weight (kg)"),
    "progress.weight_history": ("Riwayat berat", "Weight history"),
    "progress.sets": ("Set per minggu", "Sets per week"),
    "progress.sets_aria": ("Grafik jumlah set per minggu", "Total sets per week"),
    "progress.sets_empty": ("Catat latihan untuk melihat grafik.", "Log workouts to see the chart."),
    "progress.sets_note": (
        "Label menunjukkan hari Senin awal minggu. Delapan minggu terakhir.",
        "Labels show the Monday that starts each week. Last eight weeks.",
    ),
    "progress.records": ("Beban terbaik", "Best weights"),
    "progress.records_empty": ("Belum ada latihan dengan beban.", "No loaded exercises logged yet."),
}


def normalize_lang(code):
    return code if code in LANGUAGES else DEFAULT_LANGUAGE


def translate(lang, key, **values):
    """Ambil teks untuk `key`. Bila kunci tidak ada, kembalikan kuncinya (terlihat jelas saat dites)."""
    pair = S.get(key)
    if pair is None:
        return key
    text = pair[0] if lang == "id" else pair[1]
    return text.format(**values) if values else text
