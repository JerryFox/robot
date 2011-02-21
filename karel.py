import livewires

livewires.begin_graphics()
livewires.allow_movables()


class robot():

    def __init__(self,*seznam_objektu):
        self.velikost = 100
        self.orientace = 0
        self.x = 200
        self.y = 200
        self.zobrobjekty = []
        self.je_videt = False
        if len(seznam_objektu)>0:
            self.objekty = seznam_objektu[0]
        else:
            self.objekty = []
            self.objekty = [["c",0,0,0.5,livewires.Colour.red,1],["c",0.1,0.18,0.08,livewires.Colour.black,1],["c",0.1,-0.18,0.08,livewires.Colour.black,1],["p",[0.1,0,0.3,-0.1,0.3,0.1],livewires.Colour.black,1,1],["b",0.38,-0.15,0.43,0.15,livewires.Colour.black,1]]
        self.delka_kroku = self.velikost
        # identifikace města, ve kterém se robot nachází
        self.mesto = False
        # je-li robot stavitelem města
        self.je_stavitel = False
        
    def zed_na_policku(self, *nastaveni):
        ized = False
        if str(type(self.mesto)) == "<type 'instance'>":
            ized = self.mesto.zed_na_policku(self.mx, self.my, *nastaveni)
        else:
            print "robot neni ve meste"
        return ized 
    
    def stavitel(self, *nastaveni):
        if len(nastaveni) > 0:
            if nastaveni[0]:
                self.je_stavitel = True
            else:
                self.je_stavitel = False
        return self.je_stavitel
    
    def vlevo_vbok(self):
        self.orientace = (self.orientace+1)%4
        ivisible = self.je_videt
        if ivisible:
            self.skryj()
        # transformace objektů
        # x -> y
        # y -> -x
        self.objekty = self.rot90(self.objekty)
        # případné znovuzobrazení
        if ivisible:
            self.zobraz()

    def skryj(self):
        for i in self.zobrobjekty:
            livewires.remove_from_screen(i)
        self.zobrobjekty=[]
        self.je_videt = False

    def zobraz(self):
        if not self.je_videt:
            for i in self.objekty:
                self.zobrobjekty.append(self.zobraz_objekt(i))
            self.je_videt=True

    def zobraz_objekt(self,ilist):
        if ilist[0] == "c":
            i = livewires.circle(self.x + ilist[1]*self.velikost, self.y + ilist[2]*self.velikost,ilist[3]*self.velikost,*ilist[4:])
        elif ilist[0] == "b":
            i = livewires.box(self.x + ilist[1]*self.velikost, self.y + ilist[2]*self.velikost,self.x + ilist[3]*self.velikost, self.y + ilist[4]*self.velikost,*ilist[5:])
        elif ilist[0] == "p":
            i = False
            # seznam souradnic:
            ilist1 = []
            ix = True
            for j in ilist[1]:
                pass
                if ix:
                    ilist1.append(self.x + j*self.velikost)
                    ix = False
                else:
                    ilist1.append(self.y + j*self.velikost)
                    ix = True
            i = livewires.polygon(ilist1,*ilist[2:])
        return i

    def rot90(self,objekty):
        # transformace objektů
        # x -> y
        # y -> -x
        iobjekty = []
        for ilist in objekty:
            if ilist[0] == "c":
                i = ilist[2]
                ilist[2] = ilist[1]
                ilist[1] = -i
            elif ilist[0] == "b":
                i = ilist[2]
                ilist[2] = ilist[1]
                ilist[1] = -i
                i = ilist[4]
                ilist[4] = ilist[3]
                ilist[3] = -i
            elif ilist[0] == "p":
                # seznam souradnic:
                for j in range(0,len(ilist[1]),2):
                    i = ilist[1][j+1]
                    ilist[1][j+1] = ilist[1][j]
                    ilist[1][j] = -i
            iobjekty.append(ilist)
        return iobjekty

    def vpravo_vbok(self):
        ivisible = self.je_videt
        if ivisible:
            self.skryj()
        for i in range(3):
            self.vlevo_vbok()
        if ivisible:
            self.zobraz()

    def krok(self):
        ivisible = self.je_videt
        if ivisible:
            self.skryj()
        # ze směru identifikuji přírůstky v jednotlivých osách
        self.x += (self.orientace+1)%2*(1-(self.orientace/2*2))*self.delka_kroku
        self.y += self.orientace%2*(1-(self.orientace/2*2))    *self.delka_kroku
        if str(type(self.mesto)) == "<type 'instance'>":
            self.mx += (self.orientace+1)%2*(1-(self.orientace/2*2))
            self.my += self.orientace%2*(1-(self.orientace/2*2))    
        if ivisible:
            self.zobraz()

    def do_mesta(self, mesto, *dalsi_parametry):
        # umístí robota do města
        # asi to zatím bude bastl, protože všechno nebude přes řádný interface

        ivisible = self.je_videt
        if ivisible:
            self.skryj()

        self.mesto = mesto

        # implicitně umístit robota do levého dolního rohu
        # souřadnice ve městě
        self.mx = 0
        self.my = 0
        # možnost zadat souřadnice v dalsi_parametry
        if len(dalsi_parametry) >= 2:
            self.mx = dalsi_parametry[0]
            self.my = dalsi_parametry[1]

        self.delka_kroku = mesto.delka_kroku

        # informace o políčku zjistit ve městě
        i = self.mesto.sour_pole(self.mx,self.my)
        if len(i) > 0:
            self.x = (i[0]+i[2])/2
            self.y = (i[1]+i[3])/2
        else:
            print "pole", self.mx, self.my, "neni ve meste"
            
        if self.velikost > mesto.modul:
            self.velikost = (mesto.modul*8)/10
        
        if ivisible:
            self.zobraz()
        

class mesto:
    def __init__(self,*seznam):
        # volitelné parametry jsou buď:
        # rozměr vodorovně, rozměr svisle (počty políček)
        # nebo seznam objektů města determinující rozměry města
        self.objekty = []
        if len(seznam) == 0: 
            # implicitní počet políček
            self.vodorovne = 8
            self.svisle = 6
        elif type(seznam[0]) == type(0):
            # počet políček dán parametry
            self.vodorovne = seznam[0]
            self.svisle = seznam[1]
        elif type(seznam[0]) == type([]):
            # město zadáno jako seznam seznamů objektů na políčkách
            self.objekty = seznam[0]
        else:
            print "chybne inicializacni parametry"
            
        # seznamy objektů na jednotlivých políčcích města
        if self.objekty == []:
            for i in range(self.svisle):
                ir = []
                for j in range(self.vodorovne):
                    ir.append([])
                self.objekty.append(ir)
        else:
            self.svisle = len(self.objekty)
            self.vodorovne = len(self.objekty[0])
            
        # velikost vnitřku políčka
        self.modul = 60
        # čára - tloušťka, barva
        self.tl_cary = 4
        self.barva_cary = livewires.Colour.blue
        # souřadnice levého dolního rohu
        self.x = 5
        self.y = 5
        # vypočtená délka kroku
        self.delka_kroku = self.modul + self.tl_cary
        # viditelnost města
        self.je_videt = False
        # barva pozadí
        self.barva_pozadi = livewires.Colour.white 

    def zobraz(self):
        livewires.forbid_movables()
        # celé město obarvit pozadím - kvůli překreslování
        i = [self.x,self.y,
        self.x+self.vodorovne*(self.modul+self.tl_cary)+self.tl_cary,
        self.x+self.svisle*(self.modul+self.tl_cary)+self.tl_cary]
        i += [self.barva_pozadi,1]
        livewires.box(*i)
        # vodorovné čáry
        for i in range(self.svisle+1):
            livewires.box(self.x, self.y+i*(self.modul+self.tl_cary),self.x+self.tl_cary*(self.vodorovne+1)+self.modul*self.vodorovne-1, self.y+i*(self.modul+self.tl_cary)+self.tl_cary-1,self.barva_cary,1)
        livewires.allow_movables()
        # svislé čáry
        for i in range(self.vodorovne+1):
            livewires.box(self.x+i*(self.modul+self.tl_cary), self.y, self.x+i*(self.modul+self.tl_cary)+self.tl_cary-1, self.y+self.svisle*(self.tl_cary+self.modul)+self.tl_cary-1, self.barva_cary,1)
        livewires.allow_movables()

        # namaluj zdi (případně ostatní objekty)
        for irad in range(len(self.objekty)): 
            for islo in range(len(self.objekty[irad])):
                if "wall" in self.objekty[irad][islo]:
                    self.maluj_zed(islo, irad)
        self.je_videt = True

    def maluj_zed(self, pole_x, pole_y, *nastaveni):
        iparam = self.sour_pole(pole_x, pole_y)
        if len(nastaveni)>0 and nastaveni[0]==False:
            ibarva = livewires.Colour.white
        else:
            ibarva = livewires.Colour.dark_red
        iparam.append(ibarva)
        iparam.append(1)
        livewires.box(*iparam)
        

    def sour_pole(self, pole_x, pole_y):
        x0 = self.x + self.tl_cary + pole_x*(self.modul + self.tl_cary)
        y0 = self.y + self.tl_cary + pole_y*(self.modul + self.tl_cary)
        x1 = x0 + self.modul - 1
        y1 = y0 + self.modul - 1
        return [x0,y0,x1,y1]

    def zed_na_policku(self, pole_x, pole_y, *nastaveni):
        if self.je_ve_meste("pole",[pole_x, pole_y]) != False:
            je_zed = ("wall" in self.objekty[pole_y][pole_x])
            if len(nastaveni)>0:
                # postavit/zrusit zed
                if nastaveni[0] == True and not je_zed:
                    self.objekty[pole_y][pole_x].append("wall")
                    je_zed = True
                elif nastaveni[0] == False and je_zed:
                    self.objekty[pole_y][pole_x].remove("wall")
                if self.je_videt:
                    self.maluj_zed(pole_x, pole_y, nastaveni[0])
                    je_zed = False
        else:
            je_zed = True
        return je_zed

    def je_ve_meste(self, co, identifikace):
        if co == "pole":
            # zjistit je-li pole ve městě
            x = identifikace[0]
            y = identifikace[1]
            if x < 0 or y < 0 or x >= self.vodorovne or y >= self.svisle:
                vysledek = False
            else:
                vysledek = self.objekty[y][x]
        elif co == "robot":
            pass
        return vysledek

    def do_mesta(self, objekt, typ, *param):
        # žádost o přijetí objektu (robota) do města
        # nepovinné parametry:
        #   x požadované
        #   y požadované
        #   požad. prázdné pole (bez zdi)
        if type(objekt).__name__ == 'instance':
            if typ == "robot":
                if len(param)>1 and self.je_ve_meste("pole",[param[0],param[1]]) != False:
                    x0 = param[0]
                    y0 = param[1]
                else:
                    x0 = 0
                    y0 = 0
                                                      
                if len(param)>2 and param[2] == True:
                    # hledání nejbližšího volného pole
                    iodchylka = 0
                    x01 = x0
                    y01 = y0
                    while self.zed_na_policku(x01, y01) and iodchylka<max(self.vodorovne, self.svisle):
                        iodchylka += 1
                        y01 = y0 + iodchylka
                        x01 = x0 - iodchylka
                        orientace = 0
                        while self.zed_na_policku(x01, y01) and orientace < 4:
                                j = 0
                                while self.zed_na_policku(x01, y01) and j < (iodchylka*2):
                                    x01 = x01 + (orientace+1)%2*(1-(orientace/2*2))
                                    y01 = y01 + -(orientace%2*(1-(orientace/2*2)))
                                    # print x01, y01
                                    j += 1
                                orientace += 1
                    if not self.zed_na_policku(x01, y01):
                        x0 = x01
                        y0 = y01
        return [x0, y0]

    def ocisluj(self, *velikost):
        # očíslování buněk města
        if len(velikost) == 0:
            ivel = 8
        else:
            ivel = velikost[0]
        livewires.forbid_movables()
        ivel = livewires.set_textsize(ivel)
        for i in range(self.svisle):
                for j in range(self.vodorovne):
                        livewires.move(*self.sour_pole(j, i)[:2])
                        livewires.text(str([j, i]))
        ivel = livewires.set_textsize(ivel)
        livewires.allow_movables()
        
# příliš žluťoučký kůň úpěl ďábelské ódy

                       
