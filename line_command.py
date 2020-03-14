from scraper import get_table


def output(cmd):
    # format to country style First Capital
    cmd = cmd.lower()
    cmd.capitalize()

    if cmd == 'ไทย':
        return get_table('Thailand')
    elif cmd == 'ทั่วโลก':
        return get_table('world')

    # command for other country
    else:
        try:
            get_table(cmd)
        except Exception:
            return 'ไม่พบประเทศ "{}" กรุณากรอกใหม่อีกครั้งค่ะ'.format(cmd)
