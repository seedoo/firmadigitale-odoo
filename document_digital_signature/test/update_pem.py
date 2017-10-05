import erppeek


pem = """
-----BEGIN CERTIFICATE-----
MIIEaTCCA1GgAwIBAgIQLKH9fAsP9ObL02oIqPiY4jANBgkqhkiG9w0BAQsFADBs
MQswCQYDVQQGEwJJVDEYMBYGA1UECgwPQXJ1YmFQRUMgUy5wLkEuMSEwHwYDVQQL
DBhDZXJ0aWZpY2F0aW9uIEF1dGhvcml0eUMxIDAeBgNVBAMMF0FydWJhUEVDIFMu
cC5BLiBORyBDQSAzMB4XDTEzMDczMTAwMDAwMFoXDTE2MDczMDIzNTk1OVowgZcx
CzAJBgNVBAYTAklUMRUwEwYDVQQKDAxub24gcHJlc2VudGUxGjAYBgNVBAMMEVBB
U0NISU5PIExFT05BUkRPMRwwGgYDVQQFExNJVDpQU0NMUkQ4MFMyNUk0NTJSMREw
DwYDVQQqDAhMRU9OQVJETzERMA8GA1UEBAwIUEFTQ0hJTk8xETAPBgNVBC4TCDEy
MjgzOTU4MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQZUCCDph4xvZa9GEk
xvpMeKZ1+Wiwi3fV8vBI2V0Ud0blEhL18fVImuvHQfybibok4riMiKzXmv+9FP4P
BaOgjRam6LyXIlYM8cYwjHk9AwLG5WM3FE1WTdK7C6RwWKRO8hXaP7eBMW2+QTNE
A/mYIERMsFC86nsXA9bVaurkSwIDAQABo4IBXTCCAVkwDgYDVR0PAQH/BAQDAgZA
MB0GA1UdDgQWBBRTFoeki/oVV7mkKlwhHmCiegaciTBHBgNVHSAEQDA+MDwGCysG
AQQBgegtAQEBMC0wKwYIKwYBBQUHAgEWH2h0dHBzOi8vY2EuYXJ1YmFwZWMuaXQv
Y3BzLmh0bWwwWAYDVR0fBFEwTzBNoEugSYZHaHR0cDovL2NybC5hcnViYXBlYy5p
dC9BcnViYVBFQ1NwQUNlcnRpZmljYXRpb25BdXRob3JpdHlDL0xhdGVzdENSTC5j
cmwwLwYIKwYBBQUHAQMEIzAhMAgGBgQAjkYBATALBgYEAI5GAQMCARQwCAYGBACO
RgEEMB8GA1UdIwQYMBaAFPDARbG2NbTqXyn6gwNK3C/1s33oMDMGCCsGAQUFBwEB
BCcwJTAjBggrBgEFBQcwAYYXaHR0cDovL29jc3AuYXJ1YmFwZWMuaXQwDQYJKoZI
hvcNAQELBQADggEBAJJTERqP10+Tqetc4KpkTVUy6YaWF60rDjEmyUEZXehswX0T
HB1caRYgcY0DNBdiRSPSQbSJMoLwuyzUpRaWyWOckMt+g/Vm2aq8PdnRACyCxKv8
eiFaCO9e/XiTQL/QAuCqQizU7JbH4FHXlPu+XcU8v+PN6BhiWmCgKdg5FWvyj0Z0
bPq+khM+pOY1vNut+W/kNTojDx6G5phooyC5nzjElTiijE2BUyi50mILvp7me5SI
q1jH8rlP05ElS6nXMZF11xpqfOb3pVlQe4DDnQSsd3RE8X0wqQjCDXKtUCtSzaT+
oDQ1mKbjXxH4tSmPTStqOKhAo6gTdiPPXoIGR44=
-----END CERTIFICATE-----
"""


class User():
    _name = 'user.pem'

    def __init__(self):
        self.host = 'localhost'
        self.port = '80'
        self.db = 'firmadigitale'
        self.user = 'roberto'
        self.password = 'roberto'
        self.client = erppeek.Client('http://' + self.host + ':' + self.port,
                                     self.db,
                                     self.user,
                                     self.password)

    def update_pem(self):
        user_proxy = self.client.model('res.users')
        user_proxy.browse(self.client._execute.args[1])
        res = user_proxy.update_pem(pem)
        print res


if __name__ == '__main__':
    user = User()
    user.update_pem()
