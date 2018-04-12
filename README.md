TP1 - FTP
=========

Barthélémy Delemotte
M1 MIAGE FA


## Utilisation

TP réalisé avec Python 3.5.2.

Lancement du serveur (sur le port 5557):
```sh
python3.5 server.py
```

Lancement du client:
```sh
ftp -4 localhost 5557
```

## Implémentation

Chaque client est géré dans un thread.
La gestion de thread est abstraite par le package `socketserver`.


Ouverture des sockets de données uniquement en mode actif et en IPv4

Choix du mode de transfert de données : binaire ou ascii.

Gestion d'erreurs d'accès au filesystem basique.

Commandes :
* USER
* PASS
* PORT
* TYPE "A" / TYPE "I" (ascii, binary)
* DIR
* RETR
* STOR
* QUIT

Serveur extensible facilement grace aux appels de méthodes dynamiques :
```python
cmd, args = self.receive()
getattr(self, "cmd_" + cmd.lower(), self.cmd_unknown)(args)
```
... pour ajouter une commande, il suffit de créer une méthode `cmd_<nom_commande>(args)` dans la class `ClientHandler`







