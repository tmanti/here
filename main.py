import pygame
pygame.init()
#import startscreen
import Player
import db
import dataTypes
import item
import world
import json
import enemy
import methods
import random

# TODO LIST - make someone say mada mada
#for miller
# TODO LIST - hand_Okay
#for daniel

#init pygame
p = pygame

#create a database interface
dbInt = db.DBInterface()

#another shortcut
pos = dataTypes.pos

#define color constants for easy access
WHITE = dataTypes.WHITE
BLACK = dataTypes.BLACK
RED = dataTypes.RED
GREEN = dataTypes.GREEN
BLUE = dataTypes.BLUE

#easy acces to display and clock
display = p.display
clock = p.time.Clock()

#reference to the save method
save = dbInt.save

#DATA BASE METHODS
#generate new save (compiles all information then writes to db)
def GenerateNewSave(playerName, playerClass):
    player = Player.generateNewPlayerData(playerClass)
    worldData = dataTypes.worldData()

    saveData = dataTypes.saveData(player, worldData).return_save()
    dbInt.newSave(playerName, saveData)

#loads a save then return the parsed save data
def loadSave(saveName):
    save = dbInt.checkSave(saveName)
    return ParseSaveData(json.loads(save.userdata))

#parses the save data and returns it as a saveData object for easy use
def ParseSaveData(saveData):
    player = dataTypes.playerData(
        pos(saveData[0]['pos']['x'], saveData[0]['pos']['y']),
        dataTypes.playerInventory(weapon=item.ItemStack(1, item.allItems[saveData[0]['inv']['weapon']]), special=item.ItemStack(1, item.allItems[saveData[0]['inv']['special']]), armour=item.ItemStack(1, item.allItems[saveData[0]['inv']['armour']]), ring=item.ItemStack(1, item.allItems[saveData[0]['inv']['ring']]), container=dataTypes.container(30, saveData[0]['inv']['container'])),
        dataTypes.entityStats(hp=saveData[0]['stats']['hp'], mp=saveData[0]['stats']['mp'], defen=saveData[0]['stats']['def'] ,spd=saveData[0]['stats']['spd'], atk=saveData[0]['stats']['atk'], dex=saveData[0]['stats']['dex'], vit=saveData[0]['stats']['vit']),
        Player.className[saveData[0]['class']],
        dataTypes.Level(saveData[0]['level']['lvl'], saveData[0]['level']['exp'])
    )
    worldData = dataTypes.worldData(saveData[1]['seed'])

    return dataTypes.saveData(player, worldData)

#main client object
class Client:
    #define constants
    running = True

    def __init__(self):
        #initialize pygame and the screen
        self.screen = p.display.set_mode((dataTypes.w, dataTypes.h), pygame.FULLSCREEN)
        pygame.display.set_caption('Dungeon Explorer')  # Title on the title bar of the screen

        self.state = 1

        self.states = {1: self.main_menu, 2:self.game, 3:self.pause}

        #initialize items
        item.init()

        #initialize enemies
        enemy.init()

        self.name = None

        self.enemies = p.sprite.Group()
        #genned Chunks dict to easily store all genned chunks for easy reuse
        self.gennedChunks = {}

    def run(self):
        #main game loop
        while self.running:
            clock.tick(dataTypes.FPS)

            self.states[self.state]()

        #once while loop broken
        p.quit()
        return

    def main_menu(self):
        load = True

        menuState = 1 #1 is main menu, 2 is play menu

        gennedChunks = {}
        loadedChunks = []

        World = world.world(random.randint(1, 10000))

        toGen = dataTypes.pos(-1, -1)
        genTemp = dataTypes.pos(toGen.x, toGen.y)

        for y in range(3):
            genTemp.y = toGen.y + y
            genTemp.x = toGen.x
            for x in range(3):
                genTemp.x = toGen.x + x
                if str(genTemp) not in gennedChunks.keys():
                    gennedChunks[str(genTemp)] = world.Chunk(dataTypes.chunkData(genTemp))
                    gennedChunks[str(genTemp)].genChunk(World.genNoiseMap(gennedChunks[str(genTemp)].tilePos))
                loadedChunks.append(gennedChunks[str(genTemp)])

        buttons1 = p.sprite.Group()
        buttons1.add(methods.playButton(dataTypes.w//2, 400), methods.instructionsButton(dataTypes.w//2, 500), methods.backButton(dataTypes.w//2, 600, text="Exit"))

        buttons2Load = p.sprite.Group()
        buttons2NewSave = p.sprite.Group()

        buttons3 = p.sprite.Group()
        buttons3.add(methods.createSaveButton(dataTypes.w//2, dataTypes.h//4+dataTypes.h//2))
        buttons3Next = p.sprite.Group()
        buttons3Next.add(methods.nextButton(dataTypes.w//2-130, dataTypes.h//4+227, "L", fonts=[dataTypes.GUI_FONT, dataTypes.GUI_FONT_BUTTON]))
        buttons3Next.add(methods.nextButton(dataTypes.w // 2 + 75, dataTypes.h // 4 + 226, "R", fonts=[dataTypes.GUI_FONT, dataTypes.GUI_FONT_BUTTON]))
        buttons3Back = p.sprite.Group()
        buttons3Back.add(methods.backButton(dataTypes.w//2, dataTypes.h//4+dataTypes.h//2+100))

        buttons4 = p.sprite.Group(methods.backButton(dataTypes.w // 2, 100))

        saves = 5

        temp = 0

        menuSwapped = False

        accs = []

        for x in dbInt.returnAllSaves():
            buttons2Load.add(methods.loadButton(dataTypes.w // 2, 300 + temp * 100, x.name, fonts=[dataTypes.GUI_FONT, dataTypes.GUI_FONT_BUTTON]))
            accs.append(x.name)
            temp += 1
            saves -= 1

        for y in range(saves):
            buttons2NewSave.add(methods.newSaveButton(dataTypes.w//2, 300+temp*100+y*100, fonts=[dataTypes.GUI_FONT, dataTypes.GUI_FONT_BUTTON]))

        TextField = []
        classes = [Player.warriorClass, Player.mageClass, Player.rangerClass]
        classesIndex = 0

        errorMessages = []

        while load:
            for e in pygame.event.get():
                if e.type == p.QUIT:
                    quit()
                if e.type == p.KEYDOWN:
                    if e.key == p.K_ESCAPE:
                        quit()
                if e.type == p.MOUSEBUTTONDOWN and e.button == 1:  # if it is a click
                    mouse = p.mouse.get_pos()  # get mouse position
                    if not menuSwapped and menuState == 1:
                        for x in buttons1:  # for each button on screen 1
                            if (x.x + x.w > mouse[0] > x.x) and (x.y + x.h > mouse[1] > x.y):  # if it is on a button and it it is o the r
                                if x.text == 'Play':
                                    menuState = 2
                                elif x.text == 'Instructions':
                                    menuState = 4
                                elif x.text == 'Exit':
                                    load=False
                                    self.running = False
                                menuSwapped = True
                    if menuState == 2 and not menuSwapped:
                        for x in buttons2Load:
                            if (x.x + x.w > mouse[0] > x.x) and (x.y + x.h > mouse[1] > x.y):
                                self.Load(x.text)
                                load = False
                                menuSwapped = True
                        for x in buttons2NewSave:
                            if (x.x + x.w > mouse[0] > x.x) and (x.y + x.h > mouse[1] > x.y):
                                menuState = 3
                                menuSwapped = True
                                TextField = []
                    if menuState == 3 and not menuSwapped:
                        for x in buttons3:
                            if (x.x + x.w > mouse[0] > x.x) and (x.y + x.h > mouse[1] > x.y):
                                if len(TextField) > 0:
                                    if "".join(TextField) not in accs:
                                        GenerateNewSave("".join(TextField), classes[classesIndex])
                                        self.Load("".join(TextField))
                                        load=False
                        for x in buttons3Next:
                            if (x.x + x.w > mouse[0] > x.x) and (x.y + x.h > mouse[1] > x.y):
                                classesIndex = x.press(classesIndex)
                        for x in buttons3Back:
                            if (x.x + x.w > mouse[0] > x.x) and (x.y + x.h > mouse[1] > x.y):
                                TextField = []
                                classesIndex = 0
                                menuState = 2
                    if menuState == 4 and not menuSwapped:
                        for x in buttons4:
                            if p.Rect(x.x, x.y, x.w, x.h).collidepoint(mouse[0], mouse[1]):
                                menuState = 1
                                menuSwapped = True
                if menuState == 3:
                    if e.type == p.KEYDOWN:
                        if e.key == p.K_BACKSPACE:
                            if len(TextField) > 0:
                                TextField.pop()
                        elif e.key == p.K_SPACE:
                            TextField.append(" ")
                        else:
                            TextField.append(pygame.key.name(e.key))


                if e.type == p.MOUSEBUTTONUP:
                    menuSwapped = False

            clock.tick(dataTypes.FPS)

            if menuState == 1:
                for chunk in loadedChunks:
                    chunk.tileGroup.draw(self.screen)

                methods.text_to_screen("DUNGEON EXPLORER", dataTypes.w//2, 200, self.screen, font=dataTypes.GAME_FONT_BIG)
                buttons1.update(self.screen)

            elif menuState == 2:
                for chunk in loadedChunks:
                    chunk.tileGroup.draw(self.screen)
                methods.text_to_screen("DUNGEON EXPLORER", dataTypes.w // 2, 200, self.screen, font=dataTypes.GAME_FONT_BIG)
                buttons2NewSave.update(self.screen)
                buttons2Load.update(self.screen)

            elif menuState == 3:
                for chunk in loadedChunks:
                    chunk.tileGroup.draw(self.screen)
                methods.text_to_screen("Create New Character", dataTypes.w // 2, 200, self.screen, font=dataTypes.GAME_FONT_BIG)
                methods.text_to_screen("- Name -", dataTypes.w//2, dataTypes.h//4+100, self.screen, font=dataTypes.GUI_FONT)
                methods.text_to_screen("".join(TextField), dataTypes.w//2, dataTypes.h//4+150, self.screen, center=True, font=dataTypes.GUI_FONT)
                methods.text_to_screen(classes[classesIndex].name, dataTypes.w//2, dataTypes.h//4 +250, self.screen, center=True, font=dataTypes.GUI_FONT)
                buttons3.update(self.screen)
                buttons3Back.update(self.screen)
                buttons3Next.update(self.screen)
            elif menuState == 4:
                for chunk in loadedChunks:
                    chunk.tileGroup.draw(self.screen)

                methods.text_to_screen("You are placed in an infinite world.", dataTypes.w // 2, dataTypes.h // 4 + 50, self.screen, font=dataTypes.GUI_FONT)
                methods.text_to_screen("Enemies attack you, and holding", dataTypes.w // 2, dataTypes.h // 4 + 100, self.screen, font=dataTypes.GUI_FONT)
                methods.text_to_screen("left click you can fight back.", dataTypes.w // 2, dataTypes.h // 4 + 150,self.screen, font=dataTypes.GUI_FONT)
                methods.text_to_screen("The arrow keys or WASD allow you", dataTypes.w // 2, dataTypes.h // 4 + 200, self.screen, font=dataTypes.GUI_FONT)
                methods.text_to_screen("to move and avoid projectiles.",dataTypes.w // 2, dataTypes.h // 4 + 250, self.screen, font=dataTypes.GUI_FONT)
                methods.text_to_screen("Equip items enemies drop", dataTypes.w // 2, dataTypes.h // 4 + 300, self.screen, font=dataTypes.GUI_FONT)
                methods.text_to_screen("to become more powerful.", dataTypes.w // 2, dataTypes.h // 4 + 350, self.screen, font=dataTypes.GUI_FONT)
                methods.text_to_screen("Try to survive as long as possible.", dataTypes.w // 2, dataTypes.h // 4 + 400, self.screen, font=dataTypes.GUI_FONT)

                buttons4.update(self.screen)

            display.update()

        self.state = 2

    def game(self):
        #allChunks = [_.split(":") for _ in self.gennedChunks.keys()]
        #allChunks = [[int(allChunks[x][0]), int(allChunks[x][1])] for x in range(len(allChunks))]
        for e in p.event.get():  # event queue
            if e.type == p.QUIT:
                self.running = False
                if self.name:
                    dbInt.save(self.name, dataTypes.saveData(self.Player.return_playerData(), self.World.returnWorldData()).return_save())
            if e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:
                    self.state = 3
            if e.type == pygame.USEREVENT+1:
                self.Player.Fire(pygame.mouse.get_pos())

        loadedChunks = []

        self.screen.fill(dataTypes.BLACK)

        toGen = dataTypes.pos(self.Player.chunkPos.x-1, self.Player.chunkPos.y-1)
        genTemp = dataTypes.pos(toGen.x, toGen.y)

        for y in range(3):
            genTemp.y = toGen.y+y
            genTemp.x = toGen.x
            for x in range(3):
                genTemp.x = toGen.x+x
                if str(genTemp) not in self.gennedChunks.keys():
                    self.gennedChunks[str(genTemp)] = world.Chunk(dataTypes.chunkData(genTemp))
                    self.gennedChunks[str(genTemp)].genChunk(self.World.genNoiseMap(self.gennedChunks[str(genTemp)].tilePos), enemiesGroup=self.enemies)
                loadedChunks.append(self.gennedChunks[str(genTemp)])

        for chunk in loadedChunks:
            chunk.tileGroup.update(self.Player.position)
            chunk.tileGroup.draw(self.screen)

        for coords in list(self.gennedChunks):
            temp = [int(_) for _ in coords.split(":")]
            if (((temp[0] - self.Player.chunkPos.x)**2 + (temp[1] - self.Player.chunkPos.y)**2)**0.5) > 4:
                del self.gennedChunks[coords]

        self.enemies.update(self.Player.position, self.screen)
        self.enemies.draw(self.screen)
        for x in self.enemies:
            x.bullets.update(self.Player.position)
            x.bullets.draw(self.screen)

        self.Player.bullets.update(self.Player.position)
        self.Player.bullets.draw(self.screen)
        #check for colosion between bullet gorups
        #deal damage to object collided with
        hits = pygame.sprite.groupcollide(self.Player.bullets, self.enemies, False, False)
        for hit in hits:
            hits[hit][0].hit(hit.damage)

        self.Player.update(self.gennedChunks)

        self.screen.blit(self.Player.playerAnim, (dataTypes.w/2-16 + self.Player.drawOffset, dataTypes.h/2-16))

        #gui
        pygame.draw.rect(self.screen, dataTypes.GRAY, (0, 850, dataTypes.w, 150))

        if self.Player.inventory.weapon.material.image:
            self.screen.blit(self.Player.inventory.weapon.material.image, (dataTypes.w//4+100, 950))
        if self.Player.inventory.special.material.image:
            self.screen.blit(self.Player.inventory.special.material.image, (dataTypes.w//4+200, 950))
        if self.Player.inventory.armour.material.image:
            self.screen.blit(self.Player.inventory.armour.material.image, (dataTypes.w//4+300, 950))
        if self.Player.inventory.ring.material.image:
            self.screen.blit(self.Player.inventory.ring.material.image, (dataTypes.w//4+400, 950))

        p.display.update()

    def pause(self):
        load = True

        exitGame = False

        buttons = p.sprite.Group()
        buttons.add(methods.backButton(500, 550, text="Back To Menu", fonts=[dataTypes.GUI_FONT_SMALL, dataTypes.GUI_FONT_SMALLER], boxOffset=200))

        while load:
            for e in pygame.event.get():
                if e.type == p.KEYDOWN:
                    if e.key == p.K_ESCAPE:
                        load = False
                        self.state = 2
                if e.type == p.MOUSEBUTTONDOWN and e.button == 1:  # if it is a click
                    mouse = p.mouse.get_pos()  # get mouse position
                    for x in buttons:
                        if ((x.x + x.w+200) > mouse[0] > (x.x+200)) and ((x.y + x.h+200) > mouse[1] > (x.y+200)):
                            print(x.text)
                            if x.text == "Back To Menu":
                                dbInt.save(self.name, dataTypes.saveData(self.Player.return_playerData(), self.World.returnWorldData()).return_save())
                                load=False
                                self.state = 1

                methods.text_to_screen("PAUSED", dataTypes.w//2, dataTypes.h//8, self.screen, font=dataTypes.GUI_FONT_BIG)

                Inventory = pygame.Surface((600, 600))
                w, h = Inventory.get_size()

                Inventory.fill(dataTypes.DARK_GRAY)
                buttons.update(Inventory)

                pygame.draw.rect(self.screen, dataTypes.GRAY, (0, 850, dataTypes.w, 150))

                if self.Player.inventory.weapon.material.image:
                    self.screen.blit(self.Player.inventory.weapon.material.image, (dataTypes.w // 4 + 100, 950))
                if self.Player.inventory.special.material.image:
                    self.screen.blit(self.Player.inventory.special.material.image, (dataTypes.w // 4 + 200, 950))
                if self.Player.inventory.armour.material.image:
                    self.screen.blit(self.Player.inventory.armour.material.image, (dataTypes.w // 4 + 300, 950))
                if self.Player.inventory.ring.material.image:
                    self.screen.blit(self.Player.inventory.ring.material.image, (dataTypes.w // 4 + 400, 950))

                self.screen.blit(Inventory, (200, 200))

                display.flip()



    def Load(self, name):
        # TEMP - load player save
        self.saveData = loadSave(name)
        self.name = name
        #print(self.saveData.return_save())

        # create Player and world objects from passed data by the loadsave
        self.Player = Player.player(self.saveData.player)
        self.World = world.world(seed=self.saveData.world.seed)

#declaring game client
gameClient = Client()
gameClient.run()
