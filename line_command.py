from scraper import get_table


def output(cmd):
    # format to country style First Capital
    cmd = cmd.capitalize()

    if cmd == 'ไทย':
        return get_table('Thailand')
    elif cmd == 'ทั่วโลก':
        return get_table('World')

    # command for other country
    else:
        try:
            return get_table(cmd)
        except Exception:
            return 'ไม่พบประเทศ "{}"'.format(cmd)
