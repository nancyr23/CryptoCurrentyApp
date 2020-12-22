import requests
import json
from tkinter import Label, Entry, Button, messagebox, N, W, E, S, Tk, Menu
import sqlite3
import webbrowser
import threading

pycrypto = Tk()
pycrypto.title("My Crypto Portfolio")
pycrypto.iconbitmap("favicon.ico")

con = sqlite3.connect("CryptoCoin.db")
cursor_obj = con.cursor()

cursor_obj.execute(
    "CREATE TABLE IF NOT EXISTS Coin (id INTEGER PRIMARY KEY, name TEXT, amount INTEGER, price REAL)")
con.commit()


def enable_refresh(btn):
    btn.config(state='normal')


def refresh():
    my_portfolio()


def reset():
    for cell in pycrypto.winfo_children():
        cell.destroy()

    app_nav()
    app_header()
    my_portfolio()


def app_nav():

    def clear_portfolio():
        res = messagebox.askyesno(
            "Delete Portfolio", "Sure you wanna delete it...???")
        if res:
            cursor_obj.execute("DELETE FROM Coin")
            con.commit()
            timer.cancel()
            reset()
            messagebox.showinfo("Portfolio Notification",
                                "Portfolio Deleted Successfully - Add New Coins!!!")

    def close_app():
        res = messagebox.askyesno("Exit Portfolio", "Do you really wanna go?")
        if res:
            pycrypto.destroy()

    def help_url():
        res = messagebox.askokcancel(
            "Portfolio Notification", "Will redirect to browser. Is it okay?")
        if res:
            url = "https://coinmarketcap.com/"
            webbrowser.open(url, new=1)

    menu = Menu(pycrypto)

    # Ist Item
    file_menu = Menu(menu)
    file_menu.add_command(label='Clear Portfolio', command=clear_portfolio)
    file_menu.add_command(label='Close Application', command=close_app)
    menu.add_cascade(label="File", menu=file_menu)

    # IInd Item
    menu.add_cascade(label="Help", command=help_url)

    # IIIrd Item
    links_menu = Menu(menu)
    account_url = "https://pro.coinmarketcap.com/login"
    links_menu.add_command(label='API Account Page',
                           command=lambda: webbrowser.open(account_url, new=1))
    doc_url = "https://coinmarketcap.com/api/documentation/v1/"
    links_menu.add_command(label='API Documentation',
                           command=lambda: webbrowser.open(doc_url, new=1))
    test_api_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?&convert=INR&CMC_PRO_API_KEY=8c7f4bcf-8877-4ed9-8014-8b59a3d2ed3e&start=1&limit=10"
    links_menu.add_command(
        label='Test API Url', command=lambda: webbrowser.open(test_api_url, new=1))
    menu.add_cascade(label="Links", menu=links_menu)

    pycrypto.config(menu=menu)


def my_portfolio():
    api_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit=100&convert=USD&CMC_PRO_API_KEY=8c7f4bcf-8877-4ed9-8014-8b59a3d2ed3e"
    api_response = requests.get(api_url)
    response = json.loads(api_response.content)

    cursor_obj.execute("SELECT * FROM Coin")
    coins = cursor_obj.fetchall()

    def font_green_red(amt):
        if amt >= 0:
            return "green"
        return "red"

    def insert_coin():
        cursor_obj.execute("INSERT INTO Coin(name, price, amount) VALUES (?, ?, ?)",
                           (symbol_txt.get(), price_txt.get(), amount_txt.get()))
        con.commit()

        timer.cancel()
        reset()

        messagebox.showinfo("Portfolio Notification",
                            "Coin Added Successfully!")

    def update_coin():
        cursor_obj.execute("UPDATE Coin SET name=?, price=?, amount=? WHERE id=?",
                           (symbol_upd.get(), price_upd.get(), amount_upd.get(), p_id_upd.get()))
        con.commit()

        timer.cancel()
        reset()

        messagebox.showinfo("Portfolio Notification",
                            "Coin Updated Successfully!")

    def delete_coin():
        cursor_obj.execute("DELETE FROM Coin WHERE id=?", (p_id_del.get(), ))
        con.commit()

        timer.cancel()
        reset()

        messagebox.showinfo("Portfolio Notification",
                            "Coin Deleted from Portfolio!")

    profit_loss_all = 0
    total_current_value = 0
    complete_amt_paid = 0
    coin_row = 1

    for i in range(0, 100):
        for coin in coins:
            if coin[1] == response["data"][i]["symbol"]:
                total_paid = coin[2] * coin[3]
                current_value = coin[2] * \
                    response["data"][i]["quote"]["USD"]["price"]
                profit_loss_per_coin = response["data"][i]["quote"]["USD"]["price"] - coin[3]
                total_profit_loss = profit_loss_per_coin * coin[2]

                profit_loss_all += total_profit_loss
                total_current_value += current_value
                complete_amt_paid += total_paid

                portfolio_id = Label(pycrypto, text=coin[0], bg="#FBEDEC", fg="black",
                                     font=("Lato 11"), bd=2, relief="groove", padx="5", pady="5")
                portfolio_id.grid(row=coin_row, column=0, sticky=N+W+E+S)

                coin_name = Label(pycrypto, text=response["data"][i]["name"] +
                                  " (" + response["data"][i]["symbol"] + ") ", bg="#FBEDEC", fg="black", font=("Lato 11"), bd=2, padx="5", pady="5", relief="groove")
                coin_name.grid(row=coin_row, column=1, sticky=N+W+E+S)

                curr_price = Label(
                    pycrypto, text="$%.2f" % (response["data"][i]["quote"]["USD"]["price"]), bg="#FBEDEC", fg="black", font=("Lato 11"), bd=2, padx="5", pady="5", relief="groove")
                curr_price.grid(row=coin_row, column=2, sticky=N+W+E+S)

                no_coins = Label(pycrypto, text=coin[2],
                                 bg="#FBEDEC", fg="black", font=("Lato 11"), bd=2, padx="5", pady="5", relief="groove")
                no_coins.grid(row=coin_row, column=3, sticky=N+W+E+S)

                amount_paid = Label(pycrypto, text=f"${total_paid:.2f}",
                                    bg="#FBEDEC", fg="black", font=("Lato 11"), bd=2, padx="5", pady="5", relief="groove")
                amount_paid.grid(row=coin_row, column=4, sticky=N+W+E+S)

                curr_val = Label(pycrypto, text=f"${current_value:.2f}",
                                 bg="#FBEDEC", fg="black", font=("Lato 11"), bd=2, padx="5", pady="5", relief="groove")
                curr_val.grid(row=coin_row, column=5, sticky=N+W+E+S)

                pl_per_coin = Label(pycrypto, text=f"${profit_loss_per_coin:.2f}",
                                    bg="#FBEDEC", fg=font_green_red(profit_loss_per_coin), font=("Lato 11"), bd=2, padx="5", pady="5", relief="groove")
                pl_per_coin.grid(row=coin_row, column=6, sticky=N+W+E+S)

                total_pl = Label(pycrypto, text=f"${total_profit_loss:.2f}", bg="#FBEDEC", fg=font_green_red(total_profit_loss), font=(
                    "Lato 11"), bd=2, padx="5", pady="5", relief="groove")
                total_pl.grid(row=coin_row, column=7, sticky=N+W+E+S)

                coin_row += 1

                break

    empty_row = Label(pycrypto, text="")
    empty_row.grid(row=coin_row+1, column=0, sticky=N+W+E+S)

    # Insert Data Fields

    symbol_txt = Entry(pycrypto, bd=2, relief="groove")
    symbol_txt.grid(row=coin_row+2, column=1, ipady="5", ipadx="5")

    price_txt = Entry(pycrypto, bd=2, relief="groove")
    price_txt.grid(row=coin_row+2, column=2, ipady="5", ipadx="5")

    amount_txt = Entry(pycrypto, bd=2, relief="groove")
    amount_txt.grid(row=coin_row+2, column=3, ipady="5", ipadx="5")

    add_coin_btn = Button(pycrypto, text="ADD COIN", command=insert_coin, bg="#F2ADA9", fg="black", font=(
        "Lato 11"), bd=2, padx="5", pady="5", relief="groove")
    add_coin_btn.grid(row=coin_row+2, column=4, sticky=N+W+E+S)

    # Update Data Fields

    p_id_upd = Entry(pycrypto, bd=2, relief="groove")
    p_id_upd.grid(row=coin_row+3, column=0, ipady="5", ipadx="5")

    symbol_upd = Entry(pycrypto, bd=2, relief="groove")
    symbol_upd.grid(row=coin_row+3, column=1, ipady="5", ipadx="5")

    price_upd = Entry(pycrypto, bd=2, relief="groove")
    price_upd.grid(row=coin_row+3, column=2, ipady="5", ipadx="5")

    amount_upd = Entry(pycrypto, bd=2, relief="groove")
    amount_upd.grid(row=coin_row+3, column=3, ipady="5", ipadx="5")

    update_coin_btn = Button(pycrypto, text="UPDATE COIN", command=update_coin, bg="#F2ADA9", fg="black", font=(
        "Lato 11"), bd=2, padx="5", pady="5", relief="groove")
    update_coin_btn.grid(row=coin_row+3, column=4, sticky=N+W+E+S)

    # Delete Coin Data

    p_id_del = Entry(pycrypto, bd=2, relief="groove")
    p_id_del.grid(row=coin_row+4, column=0, ipady="5", ipadx="5")

    delete_coin_btn = Button(pycrypto, text="DELETE COIN", command=delete_coin, bg="#F2ADA9", fg="black", font=(
        "Lato 11"), bd=2, padx="5", pady="5", relief="groove")
    delete_coin_btn.grid(row=coin_row+4, column=4, sticky=N+W+E+S)

    complete_paid_amt = Label(pycrypto, text=f"${complete_amt_paid:.2f}", bg="#FBEDEC", fg="black", font=(
        "Lato 11"), bd=2, padx="5", pady="5", relief="groove")
    complete_paid_amt.grid(row=coin_row, column=4, sticky=N+W+E+S)

    total_curr_val = Label(pycrypto, text=f"${total_current_value:.2f}", bg="#FBEDEC", fg="black", font=(
        "Lato 11"), bd=2, padx="5", pady="5", relief="groove")
    total_curr_val.grid(row=coin_row, column=5, sticky=N+W+E+S)

    overall_pl = Label(pycrypto, text=f"${profit_loss_all:.2f}", bg="#FBEDEC", fg=font_green_red(profit_loss_all), font=(
        "Lato 11"), bd=2, padx="5", pady="5", relief="groove")
    overall_pl.grid(row=coin_row, column=7, sticky=N+W+E+S)

    empty_row = Label(pycrypto, text="")
    empty_row.grid(row=coin_row+5, column=0, sticky=N+W+E+S)

    refresh_btn = Button(pycrypto, text="REFRESH", command=refresh, bg="#F2ADA9", fg="black", font=(
        "Lato 11"), bd=2, padx="5", pady="5", relief="groove", state='disabled')
    refresh_btn.grid(row=coin_row+2, column=7, sticky=N+W+E+S)

    global timer
    timer = threading.Timer(60, lambda btn=refresh_btn: enable_refresh(btn))
    timer.start()
    print("Total Proft/Loss For Portfolio: %.2f" % profit_loss_all)


# Header Labels
def app_header():
    portfolio_id = Label(pycrypto, text="Portfolio ID", bg="#780C05", fg="white",
                         font="ComicSans 12 bold italic", bd=2, relief="groove", padx="5", pady="5")
    portfolio_id.grid(row=0, column=0, sticky=N+W+E+S)

    coin_name = Label(pycrypto, text="Coin (Symbol)", bg="#780C05", fg="white",
                      font="ComicSans 12 bold italic", bd=2, relief="groove", padx="5", pady="5")
    coin_name.grid(row=0, column=1, sticky=N+W+E+S)

    curr_price = Label(pycrypto, text="Current Price", bg="#780C05", fg="white",
                       font="ComicSans 12 bold italic", bd=2, relief="groove", padx="5", pady="5")
    curr_price.grid(row=0, column=2, sticky=N+W+E+S)

    no_coins = Label(pycrypto, text="Coins Owned", bg="#780C05", fg="white",
                     font="ComicSans 12 bold italic", bd=2, relief="groove", padx="5", pady="5")
    no_coins.grid(row=0, column=3, sticky=N+W+E+S)

    amount_paid = Label(pycrypto, text="Total Amount Paid", bg="#780C05", fg="white",
                        font="ComicSans 12 bold italic", bd=2, relief="groove", padx="5", pady="5")
    amount_paid.grid(row=0, column=4, sticky=N+W+E+S)

    curr_val = Label(pycrypto, text="Current Value", bg="#780C05", fg="white",
                     font="ComicSans 12 bold italic", bd=2, relief="groove", padx="5", pady="5")
    curr_val.grid(row=0, column=5, sticky=N+W+E+S)

    pl_per_coin = Label(pycrypto, text="Profit/Loss Per Coin", bg="#780C05", fg="white",
                        font="ComicSans 12 bold italic", bd=2, relief="groove", padx="5", pady="5")
    pl_per_coin.grid(row=0, column=6, sticky=N+W+E+S)

    total_pl = Label(pycrypto, text="Total Profit/Loss", bg="#780C05", fg="white",
                     font="ComicSans 12 bold italic", bd=2, relief="groove", padx="5", pady="5")
    total_pl.grid(row=0, column=7, sticky=N+W+E+S)


def on_closing():
    timer.cancel()
    pycrypto.destroy()


app_nav()
app_header()
my_portfolio()

pycrypto.protocol("WM_DELETE_WINDOW", on_closing)
pycrypto.mainloop()

cursor_obj.close()
con.close()


print("Program Completed!")
