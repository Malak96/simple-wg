from rich.text import Text
from textual import containers, on
from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.widgets import Button, Label, Input, Static, Select, Switch, DataTable
from textual.binding import Binding

import json

class MainAppUI(Static):
    def compose(self) -> ComposeResult:
        with containers.Container():
            yield Vertical(
                Horizontal(
                    Select([],id="instance_select",compact=True),
                    Button("Cargar",id="btnLoad",compact=True),
                    id="selectInstanceHorizontal",
                    classes="selectInstanceHorizontal"
                    #Switch(id="instance_switch")
                ),
                Vertical(
                    Label("publicKey",id ="lblPublicKey"),
                    Label("DNS",id="lblDNS"),
                    Label("EndPoint",id="lblEndPoint"),
                    Label("ListenPort",id="lblListenPort"),
                    Label("Address",id="lblAddress"),
                    classes="labelsDetailsVertical"
                ),

                Container(
                    DataTable(id="peerDataTable"),
                    Horizontal(
                        Button("Nuevo",id="btnNew",compact=True),
                        Button("Eliminar",compact=True,variant="error"),
                        classes="butonsPeerHorizontal"
                    ),
                    
                    classes="dataTableContainer"
                ),
                id="MainContainer"
            )

class SimpleWGApp(App):
    CSS_PATH = "resources/styles.css"
    TITLE = "Simple-WG" # Título de la ventana de la aplicación
    #ENABLE_COMMAND_PALETTE = False
    DATA_FILE_PATH = "resources/data.json"
    def compose(self) -> ComposeResult:
        yield MainAppUI()

    async def on_mount(self) -> None:
        await self.load_file_json(self.DATA_FILE_PATH)
        self.theme = "gruvbox"
        self.query_one("#MainContainer", Vertical).border_title = "Simple-WG" 
        self.query_one("#selectInstanceHorizontal",Horizontal).border_title = "Selecciona un nodo"
        self.selectInstance = self.query_one("#instance_select",Select)
        self.btnLoad = self.query_one("#btnLoad",Button)
        self.lblPublicKey = self.query_one("#lblPublicKey",Label)
        self.lblDNS = self.query_one("#lblDNS",Label)
        self.lblEndPoint = self.query_one("#lblEndPoint",Label)
        self.lblListenPort = self.query_one("#lblListenPort",Label)
        self.lblAddress = self.query_one("#lblAddress",Label)
        self.peerDataTable = self.query_one("#peerDataTable",DataTable)
        await self.fill_selectInstance()
        #self.load_data(self.DATA_FILE_PATH)
        self.peerDataTable.cursor_type = "row"
        self.peerDataTable.zebra_stripes = True
        self.peerDataTable.fixed_columns = 1
        self.peerDataTable.add_columns("name","address","Publickey","persistentKeepalive","dns","allowedIPs","Enable")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_actions = {
            "btnNew": self.handle_btn_new,
            "btnLoad": self.handle_btn_load,
        }
        action = button_actions.get(event.button.id)
        if action:
            action()
    #Acciones al selccionar un item en los Slecta
    async def on_select_changed(self, enven: Select.Changed)-> None:
        slect_changed = {
            "instance_select": self.selectInstance_Changed,
        }
        action = slect_changed.get(enven.select.id)
        if action:
            await action()

    async def load_file_json(self, path_json:str):
        try:
            with open (path_json, "r" , encoding="utf-8") as f:
                data = json.load(f)
            self.dataJSON = data
            if "servers" not in data:
                self.notify("No se encontro la clave 'servers'.")
        except(FileNotFoundError, json.JSONDecodeError) as e:
            self.notify("No se encontro ninguna configuracion, cree un nueva.", severity="warning")
    
    async def fill_selectInstance (self):
        #ls = [(nameServer["name"], id_) for id_, nameServer in self.dataJSON["servers"].items()]
        previousSelectItem = self.selectInstance.value or Select.BLANK
        itemsLs = [(nameServer["name"], id_) for id_, nameServer in self.dataJSON["servers"].items()]
        self.selectInstance.set_options(itemsLs)
    
    async def selectInstance_Changed(self):
        if self.selectInstance.value != Select.BLANK:
            selectServer = self.dataJSON["servers"][self.selectInstance.value]
            self.lblPublicKey.update(f"publicKey: {selectServer.get("publicKey")}")
            self.lblDNS.update(f"DNS: {selectServer.get("dns")}")
            self.lblEndPoint.update(f"EndPoint: {selectServer.get("endpoint")}")
            self.lblListenPort.update(f"ListenPort: {selectServer.get("port")}")
            self.lblAddress.update(f"Address: {selectServer.get("address")}")

            self.peerDataTable.clear()
            #clientsROWS=[(id_, Text(client.get("name"),key=id_), client.get("address"),client.get("publicKey"), "Si" if client.get("enable") == True else "No") for id_, client in selectServer["clients"].items()]
            
            for id_, client in selectServer.get("clients", {}).items():
                # Los datos para la fila. La 'key' se pasa por separado.
                row_data = (
                    client.get("name"),
                    client.get("address"),
                    client.get("publicKey"),
                    client.get("persistentKeepalive"),
                    client.get("dns"),
                    client.get("allowedIPs"),
                    "Sí" if client.get("enable") else "No"
                )
                # Agregamos la fila con su 'key' única
                self.peerDataTable.add_row(*row_data, key=id_)


            
            #self.peerDataTable.fixed_columns = 1
            #self.peerDataTable.add_rows(*clientsROWS)
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # 'event.row_key.value' te da directamente la clave de la fila
        selected_row_key = event.row_key.value
        self.notify(f"ID de la fila seleccionada: {selected_row_key}")



    def handle_btn_new(self):
        pass
        row_key,_ = self.peerDataTable.coordinate_to_cell_key(self.peerDataTable.cursor_coordinate)
        self.notify(str(row_key))
        #self.notify(str(xx))
        #self.peerDataTable.remove_row(self.peerDataTable.cursor_row_key)
    
    def handle_btn_load(self):
        self.notify("Mensajito")

if __name__ == "__main__":
    app = SimpleWGApp()
    app.run()