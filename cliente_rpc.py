import xmlrpc.client

def main():
    # Conexión al servidor RPC
    proxy = xmlrpc.client.ServerProxy("http://localhost:8000/", allow_none=True)


if __name__ == "__main__":
    main()