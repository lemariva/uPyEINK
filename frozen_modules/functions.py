def seconds_to_text(secs, timezone):
    secs = secs + timezone
    days = secs//86400
    hours = (secs - days*86400)//3600
    minutes = (secs - days*86400 - hours*3600)//60
    seconds = secs - days*86400 - hours*3600 - minutes*60
    #result = ("{0} day{1}, ".format(days, "s" if days!=1 else "") if days else "") + \
    result = "{0}:{1}:{2}".format(hours, minutes, seconds)
    return result

def replace_unicode(text):
    new_string = text.replace('\xc4', 'AE')
    new_string = new_string.replace('\xe4', 'ae')
    new_string = new_string.replace('\xf6', 'oe')
    new_string = new_string.replace('\xd6', 'OE')
    new_string = new_string.replace('\xdc', 'UE')
    new_string = new_string.replace('\xfc', 'ue')
    new_string = new_string.replace('\xdf', 'ss')
    new_string = new_string.replace('\u201e', '"')
    new_string = new_string.replace('\u201c', '"')
    new_string = new_string.replace('\u2026', '...')
    new_string = new_string.replace('\u2018', '\'')
    new_string = new_string.replace('\xad', '-')
    new_string = new_string.replace('\u2013', '-')
    new_string = new_string.replace('\r', ' ')
    new_string = new_string.replace('\n', ' ')
    return new_string
