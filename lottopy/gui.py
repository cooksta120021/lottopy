import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from .games import available_games, get_game_config
from .pipeline import run_game_flow


def run_gui() -> None:
    root = tk.Tk()
    root.title("LottoPy GUI")
    root.geometry("420x280")

    main_frame = ttk.Frame(root, padding=12)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Game selection
    ttk.Label(main_frame, text="Game:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=4)
    game_var = tk.StringVar(value="mega_millions")
    game_combo = ttk.Combobox(main_frame, textvariable=game_var, state="readonly", values=tuple(available_games()))
    game_combo.grid(row=0, column=1, sticky=tk.EW, pady=4)

    # Output directory
    ttk.Label(main_frame, text="Output dir:").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=4)
    output_var = tk.StringVar(value=str(Path("data").resolve()))
    output_entry = ttk.Entry(main_frame, textvariable=output_var)
    output_entry.grid(row=1, column=1, sticky=tk.EW, pady=4)

    def choose_dir() -> None:
        selected = filedialog.askdirectory()
        if selected:
            output_var.set(selected)

    ttk.Button(main_frame, text="Browse", command=choose_dir).grid(row=1, column=2, padx=(8, 0), pady=4)

    # Threshold divisor
    ttk.Label(main_frame, text="Threshold divisor:").grid(row=2, column=0, sticky=tk.W, padx=(0, 8), pady=4)
    threshold_var = tk.StringVar(value="31")
    threshold_entry = ttk.Entry(main_frame, textvariable=threshold_var, width=10)
    threshold_entry.grid(row=2, column=1, sticky=tk.W, pady=4)

    # Suggestion sets
    ttk.Label(main_frame, text="Suggestion sets:").grid(row=3, column=0, sticky=tk.W, padx=(0, 8), pady=4)
    suggestions_var = tk.StringVar(value="5")
    suggestions_entry = ttk.Entry(main_frame, textvariable=suggestions_var, width=10)
    suggestions_entry.grid(row=3, column=1, sticky=tk.W, pady=4)

    # Status display
    status_var = tk.StringVar(value="Idle")
    status_label = ttk.Label(main_frame, textvariable=status_var, foreground="blue")
    status_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(12, 4))

    # Log box
    log = tk.Text(main_frame, height=4, state="disabled", wrap="word")
    log.grid(row=6, column=0, columnspan=3, sticky=tk.NSEW, pady=(4, 0))

    # Results box
    ttk.Label(main_frame, text="Results:").grid(row=7, column=0, sticky=tk.W, pady=(8, 2))
    results = tk.Text(main_frame, height=6, state="disabled", wrap="word")
    results.grid(row=8, column=0, columnspan=3, sticky=tk.NSEW, pady=(0, 0))

    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(6, weight=1)
    main_frame.rowconfigure(8, weight=1)

    def append_log(message: str) -> None:
        log.configure(state="normal")
        log.insert(tk.END, message + "\n")
        log.see(tk.END)
        log.configure(state="disabled")

    def run_pipeline() -> None:
        try:
            status_var.set("Running...")
            root.update_idletasks()

            game_key = game_var.get()
            output_dir = Path(output_var.get()).expanduser()

            try:
                threshold = float(threshold_var.get())
            except ValueError:
                raise ValueError("Threshold divisor must be a number")

            try:
                suggestion_sets = int(suggestions_var.get())
            except ValueError:
                raise ValueError("Suggestion sets must be an integer")

            run_game_flow(
                game_key=game_key,
                output_dir=output_dir,
                threshold_divisor=threshold,
                suggestion_sets=suggestion_sets,
            )

            append_log(f"Finished {game_key}. Outputs saved to {output_dir.resolve()}")
            status_var.set("Done")
        except Exception as exc:  # noqa: BLE001
            status_var.set("Error")
            messagebox.showerror("Error", str(exc))
            append_log(f"Error: {exc}")

    def load_results() -> None:
        game_key = game_var.get()
        output_dir = Path(output_var.get()).expanduser()
        suggestions_file = output_dir / f"{game_key}_suggestions.txt"
        if not suggestions_file.exists():
            messagebox.showinfo("Not found", f"No suggestions file at {suggestions_file}")  # noqa: E501
            return
        content = suggestions_file.read_text(encoding="utf-8")
        results.configure(state="normal")
        results.delete("1.0", tk.END)
        results.insert(tk.END, content)
        results.configure(state="disabled")
        append_log(f"Loaded {suggestions_file}")

    ttk.Button(main_frame, text="Run", command=run_pipeline).grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(8, 4))
    ttk.Button(main_frame, text="Load results", command=load_results).grid(row=4, column=2, sticky=tk.EW, pady=(8, 4))

    root.mainloop()


if __name__ == "__main__":
    run_gui()
