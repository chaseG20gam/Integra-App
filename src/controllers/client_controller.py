# client crud operations management

from __future__ import annotations

from datetime import date
from typing import List, Optional

from PyQt6.QtCore import QObject, pyqtSignal as Signal
from sqlalchemy.exc import SQLAlchemyError

from models.client import Client
from models.database import session_scope

class ClientController(QObject):
    # controller for client ooperations between ui and db
    
    # signals to notify ui of changes
    clients_loaded = Signal(list)
    client_added = Signal(object)
    client_updated = Signal(object)
    client_deleted = Signal(int)
    error_ocurred = Signal(str)
    
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        
    def load_all_clients(self) -> None:
        # load all clients from database and send signal
        
        try:
            with session_scope() as session:
                clients = session.query(Client).all()
                self.clients_loaded.emit(clients)
        except SQLAlchemyError as e:
            self.error_ocurred.emit(f"No se ha conseguido cargar el cliente: {str(e)}")
            
            
    def add_client(self, 
                   first_name: str, 
                   last_name: str,
                   phone: Optional[str] = None,
                   email: Optional[str] = None,
                   birth_date: Optional[date] = None,
                   occupation: Optional[str] = None,
                   therapy_price: Optional[float] = None,
                   sports: Optional[str] = None,
                   background: Optional[str] = None,
                   observations: Optional[str] = None) -> None:
        
        # add new client
        try:
            with session_scope() as session:
                client = Client(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    birth_date=birth_date,
                    occupation=occupation,
                    therapy_price=therapy_price,
                    sports=sports,
                    background=background,
                    observations=observations
                )
                session.add(client)
                session.flush() # get the id before the commit
                self.client_added.emit(client)
        except SQLAlchemyError as e:
            self.error_ocurred.emit(f"No se ha conseguido añadir el cliente : {str(e)}")
            
    def update_client(self, client_id: int, first_name: str, last_name: str,
                      phone: Optional[str] = None, email: Optional[str] = None,
                      birth_date: Optional[date] = None, occupation: Optional[str] = None, 
                      therapy_price: Optional[float] = None, sports: Optional[str] = None, 
                      background: Optional[str] = None, observations: Optional[str] = None) -> None:
        # update existing client
        print(f"UPDATE CLIENT CALLED: ID={client_id}, name={first_name} {last_name}") # debugging
        try:
            with session_scope() as session:
                client = session.query(Client).filter(Client.id == client_id).first()
                print(f"Found client: {client}")
                if client:
                    print(f"Before update: {client.first_name} {client.last_name}")
                    client.first_name = first_name
                    client.last_name = last_name
                    client.phone = phone
                    client.email = email
                    client.birth_date = birth_date
                    client.occupation = occupation
                    client.therapy_price = therapy_price
                    client.sports = sports
                    client.background = background
                    client.observations = observations
                    print(f"After update: {client.first_name} {client.last_name}")
                    # Force commit
                    session.commit()
                    print("Session committed")
                    self.client_updated.emit(client)
                    print("Signal emitted")
                else:
                    print("Client not found!")
                    self.error_ocurred.emit(f"Client with ID {client_id} not found")
        except SQLAlchemyError as e:
            self.error_ocurred.emit(f"Failed to update client: {str(e)}")
            
    def delete_client(self, client_id: int) -> None:
        # delete a client from the database
        try:
            with session_scope() as session:
                client = session.query(Client).filter(Client.id == client_id).first()
                if client:
                    session.delete(client)
                    self.client_deleted.emit(client_id)
                else:
                    self.error_ocurred.emit(f"Client with ID {client_id} not found")
        except SQLAlchemyError as e:
            self.error_ocurred.emit(f"Failed to delete client: {str(e)}")

    def search_clients(self, query: str) -> None:
        # search clients for name or email
        try:
            with session_scope() as session:
                clients = session.query(Client).filter(
                    (Client.first_name.ilike(f"%{query}%")) |
                    (Client.last_name.ilike(f"%{query}%")) |
                    (Client.email.ilike(f"%{query}%"))
                ).all()
                self.clients_loaded.emit(clients)
        except SQLAlchemyError as e:
            self.error_ocurred.emit(f"Failed to search clients: {str(e)}")