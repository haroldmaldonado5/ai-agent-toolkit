"""
Google Drive Helper - Reutilizable para todos los módulos
Wrapper sobre Google Drive API para simplificar operaciones comunes
"""

import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Scopes necesarios para Drive y Docs
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets'
]

# Rutas de configuración
CREDENTIALS_PATH = os.path.expanduser('~/.config/google-drive-mcp/gcp-oauth.keys.json')
TOKEN_PATH = os.path.expanduser('~/.config/google-drive-mcp/tokens.pickle')


def get_credentials():
    """Obtiene o genera credenciales de Google OAuth - Reutilizable"""
    creds = None
    
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


def get_drive_service():
    """Retorna servicio de Google Drive autenticado"""
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)


def get_docs_service():
    """Retorna servicio de Google Docs autenticado"""
    creds = get_credentials()
    return build('docs', 'v1', credentials=creds)


def get_sheets_service():
    """Retorna servicio de Google Sheets autenticado"""
    creds = get_credentials()
    return build('sheets', 'v4', credentials=creds)


def create_folder(folder_name, parent_id=None):
    """Crea una carpeta en Google Drive"""
    service = get_drive_service()
    
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_id:
        file_metadata['parents'] = [parent_id]
    
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')


def upload_file(file_path, folder_id=None):
    """Sube un archivo a Google Drive"""
    service = get_drive_service()
    
    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name}
    
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    return file.get('id'), file.get('webViewLink')


def list_files(folder_id=None, query=None):
    """Lista archivos en Google Drive"""
    service = get_drive_service()
    
    if not query and folder_id:
        query = f"'{folder_id}' in parents"
    
    results = service.files().list(
        q=query,
        pageSize=100,
        fields="files(id, name, mimeType, createdTime, webViewLink)"
    ).execute()
    
    return results.get('files', [])


if __name__ == '__main__':
    # Test básico
    print('🔐 Autenticando con Google...')
    creds = get_credentials()
    print('✅ Autenticación exitosa!')
    
    print('📁 Probando acceso a Drive...')
    files = list_files()
    print(f'✅ Acceso a Drive OK - {len(files)} archivos encontrados')