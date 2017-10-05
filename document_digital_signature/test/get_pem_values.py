from datetime import datetime
import subprocess
import locale

DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_SERVER_TIME_FORMAT = "%H:%M:%S"
DEFAULT_SERVER_DATETIME_FORMAT = "%s %s" % (
    DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_TIME_FORMAT)


def get_values():
    print locale.getdefaultlocale()
    filename_in = './offerta.pdf.p7m'
    verify_arguments = ('openssl',
                        'pkcs7',
                        '-inform',
                        'DER',
                        '-in',
                        filename_in,
                        '-print_certs',
                        '-text',
                        '-out',
                        'certificate.txt')
    ret_verify = subprocess.call(verify_arguments)
    print 'ret_verify: ' + str(ret_verify)
    with open('certificate.txt', 'r') as certificate:
        pem = ""
        is_pem = False
        for line in certificate.readlines():
            if 'Not Before' in line:
                not_before = line.split(': ')[1].replace('\n', '').strip()
                date_start = datetime.strptime(
                    not_before,
                    '%b %d %H:%M:%S %Y GMT'
                )
                print date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            elif 'Not After' in line:
                not_after = line.split(': ')[1].replace('\n', '').strip()
                date_end = datetime.strptime(
                    not_after,
                    '%b %d %H:%M:%S %Y GMT'
                )
                print date_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            elif '-----BEGIN CERTIFICATE-----' in line:
                pem += line
                is_pem = True
            elif '-----END CERTIFICATE-----' in line:
                pem += line
                is_pem = False
            else:
                if is_pem:
                    pem += line
        print pem
        certificate.close()
    return True

if __name__ == "__main__":
    get_values()
