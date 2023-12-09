import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import pandas as pd

class GinTastingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gin Tasting Bewertung")
        self.root.geometry("800x600")

        self.known_gins = self.load_known_gins()

        self.num_gins = 0
        self.gins = []
        self.gin_names = {}
        self.rater_names = []
        self.ratings = {}
        self.comments = {}

        self.init_data_input()

    def load_known_gins(self):
        with open('known_gins.txt', 'r', encoding='utf-8') as file:
            known_gins = [line.strip() for line in file]
        return known_gins

    def init_data_input(self):
        input_window = tk.Toplevel(self.root)
        input_window.title("Eingabe der Anzahl Gins und Bewerter")

        tk.Label(input_window, text="Anzahl der zu testenden Gins:", font=('Arial', 12)).pack(padx=20, pady=10)
        self.num_gins = simpledialog.askinteger("Anzahl Gins", "Anzahl der zu testenden Gins:", minvalue=1, maxvalue=20)

        tk.Label(input_window, text="Anzahl der Bewerter (1-5):", font=('Arial', 12)).pack(padx=20, pady=10)
        num_raters = simpledialog.askinteger("Anzahl Bewerter", "Anzahl der Bewerter (1-5):", minvalue=1, maxvalue=5)

        for i in range(num_raters):
            name = simpledialog.askstring("Bewerter Name", f"Name des Bewerter {i+1}:")
            self.rater_names.append(name)
            self.ratings[name] = {gin: 5 for gin in self.gins}
            for gin in self.gins:
                self.comments[gin][name] = ""

        self.initUI()

    def initUI(self):
        self.layout = tk.Frame(self.root, bg='white')
        self.layout.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        header_frame = tk.Frame(self.layout, bg='white')
        header_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(header_frame, text="Gin", bg='white', fg='black', font=('Arial', 12, 'bold')).pack(side='left', padx=20)

        for rater in self.rater_names:
            tk.Label(header_frame, text=rater, bg='white', fg='black', font=('Arial', 12, 'bold')).pack(side='left', padx=30)

        self.gins = [f"Gin {i+1}" for i in range(self.num_gins)]
        self.gin_names = {gin: gin for gin in self.gins}
        self.comments = {gin: {name: "" for name in self.rater_names} for gin in self.gins}

        for gin in self.gins:
            frame = tk.Frame(self.layout, bg='white')
            frame.pack(fill='x', padx=5, pady=5)
            tk.Label(frame, text=gin, bg='white', fg='black', font=('Arial', 12)).pack(side='left', padx=20)

            for rater in self.rater_names:
                scale = tk.Scale(frame, from_=1, to=10, orient='horizontal', bg='white', fg='black')
                scale.set(5)
                scale.pack(side='left', padx=10)
                self.ratings[rater][gin] = scale

        tk.Button(self.layout, text="Kommentare hinzufügen", command=self.add_comments, bg='light gray').pack(pady=5)
        tk.Button(self.layout, text="Gin Namen auflösen", command=self.resolve_gin_names, bg='light gray').pack(pady=5)
        tk.Button(self.layout, text="Ergebnisse anzeigen", command=self.show_results, bg='light gray').pack(pady=5)
        tk.Button(self.layout, text="Graphik anzeigen", command=self.create_graphs, bg='light gray').pack(pady=5)
        tk.Button(self.layout, text="Speichern", command=self.save_data, bg='light gray').pack(pady=5)

    def add_comments(self):
        for gin in self.gins:
            for rater in self.rater_names:
                comment = simpledialog.askstring("Kommentar", f"Kommentar von {rater} für {gin}:")
                if comment:
                    self.comments[gin][rater] = comment

    def resolve_gin_names(self):
        for gin in self.gins:
            win = tk.Toplevel()
            win.title("Gin Name auswählen")

            ttk.Label(win, text=f"Wähle oder gib einen Namen für {gin} ein:").pack(padx=10, pady=5)
            combo = ttk.Combobox(win, values=self.known_gins + ["Eigener Name..."])
            combo.pack(padx=10, pady=5)
            combo.set(self.gin_names[gin])

            def confirm():
                name = combo.get()
                if name == "Eigener Name...":
                    name = simpledialog.askstring("Eigener Name", "Gib den eigenen Namen ein:", parent=win)
                self.gin_names[gin] = name
                win.destroy()

            ttk.Button(win, text="Bestätigen", command=confirm).pack(pady=5)
            self.root.wait_window(win)

    def create_graphs(self):
        scores = {self.gin_names[gin]: sum(self.ratings[rater][gin].get() for rater in self.rater_names) for gin in self.gins}
        self.show_graph(scores)
        self.show_podium(scores)

    def show_graph(self, scores):
        graph_win = tk.Toplevel()
        graph_win.title("Gin Bewertungen - Balkendiagramm")

        names = list(scores.keys())
        values = list(scores.values())

        fig, ax = plt.subplots()
        ax.bar(names, values, color='skyblue')
        ax.set_ylabel('Gesamtpunktzahl', fontsize=14)
        ax.set_title('Gin Bewertungen', fontsize=16)
        ax.set_xticklabels(names, rotation=45, ha="right", fontsize=12)

        canvas = FigureCanvasTkAgg(fig, master=graph_win)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()
        canvas.draw()

    def show_podium(self, scores):
        podium_win = tk.Toplevel()
        podium_win.title("Gin Bewertungen - Siegestreppe")

        top_3 = sorted(scores, key=scores.get, reverse=True)[:3]
        top_3_scores = [scores[gin] for gin in top_3]

        fig, ax = plt.subplots()
        ax.bar(top_3, top_3_scores, color=['gold', 'silver', 'bronze'])
        ax.set_title('Top 3 Gins', fontsize=16)
        ax.set_ylabel('Punktzahl', fontsize=14)

        canvas = FigureCanvasTkAgg(fig, master=podium_win)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()
        canvas.draw()

    def show_results(self):
        results = {self.gin_names[gin]: sum(self.ratings[rater][gin].get() for rater in self.rater_names) for gin in self.gins}
        sorted_gins = sorted(results, key=results.get, reverse=True)

        result_str = "Gesamtranking:\n"
        result_str += "\n".join([f"{gin}: {results[gin]} Punkte" for gin in sorted_gins])

        messagebox.showinfo("Ergebnisse", result_str)

    def save_data(self):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

        data = {'Gin': [], 'Bewerter': [], 'Bewertung': [], 'Kommentar': []}
        for gin in self.gins:
            for rater in self.rater_names:
                data['Gin'].append(self.gin_names[gin])
                data['Bewerter'].append(rater)
                data['Bewertung'].append(self.ratings[rater][gin].get())
                data['Kommentar'].append(self.comments[gin][rater])

        df = pd.DataFrame(data)

        file_type = simpledialog.askstring("Dateityp auswählen", "Excel oder CSV wählen:", initialvalue="Excel")
        if file_type and (file_type.lower() == "excel" or file_type.lower() == "csv"):
            filename = f"gin_tasting_{timestamp}.{file_type.lower()}"
            if file_type.lower() == "excel":
                df.to_excel(filename, index=False)
            else:
                df.to_csv(filename, index=False)

            messagebox.showinfo("Speichern abgeschlossen", f"Daten wurden als {file_type} gespeichert: {filename}")
        else:
            messagebox.showwarning("Ungültiger Dateityp", "Bitte wählen Sie 'Excel' oder 'CSV'.")

if __name__ == '__main__':
    root = tk.Tk()
    root.configure(bg='white')
    app = GinTastingApp(root)
    root.mainloop()
