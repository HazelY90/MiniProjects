import tkinter as tk
import sys
from pathlib import Path
from tkinter import messagebox
from game import Game


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return str(Path(base_path) / relative_path)


class Minesweeper:

    COLORS={          
            1: "blue",
            2: "green",
            3: "red",
            4: "darkblue",
            5: "darkred",
            6: "cyan",
            7: "black",
            8: "gray"
        }

    MODES={
        "easy":(9,9,10),
        "median":(16,16,40),
        "hard":(16,30,99),
        "professional":(20,30,126)
    }

    def __init__(self):
        self.root=tk.Tk()
        self.root.geometry("")
        self.root.title("Mine Sweeper")

        # create the menu bar
        self.menubar=tk.Menu()
        self.filemenu=tk.Menu(self.menubar,tearoff=0)
        self.filemenu.add_command(label="Restart",command=self.restart)
        self.menubar.add_cascade(menu=self.filemenu,label="File")

        self.modemenu=tk.Menu(self.menubar,tearoff=0)
        self.modemenu.add_command(label="Easy",command=self.easymode)
        self.modemenu.add_command(label="Median",command=self.medianmode)
        self.modemenu.add_command(label="Hard",command=self.hardmode)
        self.modemenu.add_command(label="Professional",command=self.professionalmode)
        self.menubar.add_cascade(menu=self.modemenu,label="Mode")

        self.root.config(menu=self.menubar)

        # create information labels
        self.topframe=tk.Frame(self.root)
        self.topframe.columnconfigure(0,weight=1)
        self.topframe.columnconfigure(1,weight=1)
        self.topframe.columnconfigure(2,weight=1)
        self.topframe.rowconfigure(0,weight=1)
        self.topframe.rowconfigure(1,weight=2)
        
        self.modelabel=tk.Label(self.topframe,text="Easy Mode",font=("Arial",14),bd=1,relief="ridge",width=26,padx=10, pady=5)
        self.modelabel.grid(row=0,column=0,columnspan=2)
        self.lifelabel=tk.Label(self.topframe,text="Lives:3",font=("Arial",14),bd=1,relief="ridge",width=12,padx=10, pady=5)
        self.lifelabel.grid(row=1,column=0)
        self.timelabel=tk.Label(self.topframe,text="Time: 00:00",font=("Arial",14),bd=1,relief="ridge",width=12,padx=10, pady=5)
        self.timelabel.grid(row=1,column=1)
        self.rebtn=tk.Button(self.topframe,text="Restart",width=10,font=("Arial",14),command=self.restart)
        self.rebtn.grid(row=0,column=2,padx=10)
        self.pausebtn=tk.Button(self.topframe,text="Pause",width=10,font=("Arial",14),command=self.pause_resume)
        self.pausebtn.grid(row=1,column=2,padx=10)
        
        self.topframe.pack(pady=10)

        #load pictures
        self.mine_img=[
            tk.PhotoImage(file=resource_path("mine0.png")),
            tk.PhotoImage(file=resource_path("mine1.png")),
        ]
        self.cell_width=max(image.width() for image in self.mine_img)
        self.cell_height=max(image.height() for image in self.mine_img)

        # create easy-mode mine area
        self.mode="easy"
        self.minearea=None
        self.easymode()

        # start showing time
        self.timer_id = None  
        self.update_timer()

        self.root.mainloop()

    def easymode(self):
        self.mode="easy"
        self.modelabel.config(text="Easy mode")
        self.create_minearea(*self.MODES[self.mode])
        self.newgame()

    def medianmode(self):
        self.mode="median"
        self.modelabel.config(text="Median mode")
        self.create_minearea(*self.MODES[self.mode])
        self.newgame()

    def hardmode(self):
        self.mode="hard"
        self.modelabel.config(text="Hard mode")
        self.create_minearea(*self.MODES[self.mode])
        self.newgame()
    
    def professionalmode(self):
        self.root.state('zoomed')
        self.mode="professional"
        self.modelabel.config(text="Professional mode")
        self.create_minearea(*self.MODES[self.mode])
        self.newgame()

    def create_minearea(self,m,n,k):
        # create the mine area.
        if self.minearea:
            self.minearea.destroy()
        self.minearea=tk.Frame(self.root)
        for i in range(m):
            self.minearea.rowconfigure(i,weight=1,uniform="rou_group")
        for j in range(n):
            self.minearea.columnconfigure(j,weight=1,uniform="column_group")
        self.buttons=[[] for _ in range(m)]
        for i in range(m):
            for j in range(n):
                self.button=tk.Canvas(
                    self.minearea,
                    width=self.cell_width,
                    height=self.cell_height,
                    bg="SystemButtonFace",
                    highlightthickness=0,
                )
                self.button.grid(row=i,column=j)
                self.button.bind("<Button-1>", lambda event, r=i, c=j: self.left_click(event, r, c))
                self.button.bind("<Button-3>", lambda event, r=i, c=j: self.flagcell(r, c))
                self.button.bind("<Button-2>", lambda event, r=i, c=j: self.flagcell(r, c))
                self.button.bind("<Control-Button-1>", lambda event, r=i, c=j: self.flagcell(r, c))
                self.draw_closed_cell(self.button)
                self.buttons[i].append(self.button)
        self.flags=[[False for _ in range(n)] for _ in range(m)]
        self.minearea.pack(padx=30,pady=20)

    def newgame(self):          
        self.game=Game(*self.MODES[self.mode])
        self.flags=[[False for _ in range(self.game.cols)] for _ in range(self.game.rows)]
        self.lifelabel.config(text=f"Lives:{self.game.lives}")
        self.timelabel.config(text="Time: 00:00")

    def left_click(self,event,i,j):
        if event.state & 0x4:
            return self.flagcell(i,j)
        self.opencell(i,j)

    def opencell(self,i,j):
        if self.game.opened[i][j] or self.flags[i][j]:
            return
        status,cells=self.game.check_status(i,j)
        if status=="lost":
            self.show_mines("fail")
            self.root.update()
            messagebox.showinfo("Failed!","Boom! Out of lives. Game Over.")
            return
        elif status=="revive":
            self.show_mine_image(i,j,0)
            self.root.update()
            res=messagebox.askyesno("Hint!","Mine Hit! Spend a life to continue?")
            if res:
                self.game.resume()
                self.reset_cell(i,j)
                self.lifelabel.config(text=f"Lives:{self.game.lives}")
            else:
                self.show_mines("fail")
                self.root.update()
                messagebox.showinfo("Failed!","Better luck next time!")
                return
        else:
            for (r,c) in cells:   
                if self.game.boards[r][c]==0:
                    self.draw_open_cell(r,c)
                else:
                    self.draw_open_cell(r,c,self.game.boards[r][c])
                
            if status=="win":
                self.show_mines("win")
                self.root.update()
                messagebox.showinfo("Congratulations!","Congratulations! You have won the game!")

    def flagcell(self,i,j):
        if self.game.opened[i][j]:
            return
        if not self.flags[i][j]:
            self.flags[i][j]=True
            self.draw_flag_cell(i,j)
        else:
            self.flags[i][j]=False
            self.reset_cell(i,j)
        return "break"

    def reset_cell(self,i,j):
        self.buttons[i][j].delete("all")
        self.draw_closed_cell(self.buttons[i][j])
        if hasattr(self,"flags"):
            self.flags[i][j]=False

    def draw_closed_cell(self,cell):
        cell.create_rectangle(0,0,self.cell_width,self.cell_height,fill="SystemButtonFace",outline="gray60")
        cell.create_line(0,0,self.cell_width,0,fill="white",width=2)
        cell.create_line(0,0,0,self.cell_height,fill="white",width=2)
        cell.create_line(0,self.cell_height-1,self.cell_width,self.cell_height-1,fill="gray45",width=2)
        cell.create_line(self.cell_width-1,0,self.cell_width-1,self.cell_height,fill="gray45",width=2)

    def draw_open_cell(self,i,j,number=None):
        self.flags[i][j]=False
        cell=self.buttons[i][j]
        cell.delete("all")
        cell.create_rectangle(0,0,self.cell_width,self.cell_height,fill="gray85",outline="gray60")
        if number:
            cell.create_text(
                self.cell_width//2,
                self.cell_height//2,
                text=str(number),
                fill=self.COLORS[number],
                font=("Arial",14,"bold"),
            )

    def draw_flag_cell(self,i,j):
        cell=self.buttons[i][j]
        cell.delete("all")
        self.draw_closed_cell(cell)
        cell.create_text(
            self.cell_width//2,
            self.cell_height//2,
            text="🚩",
            fill="red",
            font=("Arial",14),
        )

    def show_mine_image(self,i,j,image_index):
        image=self.mine_img[image_index]
        cell=self.buttons[i][j]
        cell.delete("all")
        cell.create_rectangle(0,0,self.cell_width,self.cell_height,fill="gray85",outline="gray60")
        cell.create_image(self.cell_width//2,self.cell_height//2,image=image)
   
    def show_mines(self,result):
        if result=="fail":
            for r,c in self.game.mines:
                self.show_mine_image(r,c,1)
        else:
            for r,c in self.game.mines:
                self.show_mine_image(r,c,0)
    
    def update_timer(self):
        time=self.game.update_time()
        if time:
            self.timelabel.config(text=f"Time: {time}")
            self.timelabel.update_idletasks()
        self.timer_id = self.root.after(1000, self.update_timer)
    
    def pause_resume(self):

        if self.game.time_running and self.pausebtn['text']=="Pause":
            self.game.pause()
            self.timer_id=None
            self.pausebtn.config(text='Resume')
        elif self.pausebtn['text']=='Resume' and not self.game.time_running:
            self.game.resume()
            self.update_timer()
            self.pausebtn.config(text='Pause')

    def restart(self):
        m=self.MODES[self.mode][0]
        n=self.MODES[self.mode][1]
        for i in range(m):
            for j in range(n):
                self.reset_cell(i,j)
        self.newgame()
    
