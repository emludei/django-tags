

def parse_tagstring(tagstring, separator=','):
    def valid_tag(tag):
        if not tag[0].isalpha() or len(tag) < 3:
            return False

        for word in tag.split():
            if not word.isalnum():
                return False
        return True

    tags = []

    if tagstring:
        tagstring = tagstring.lower().strip()
        if not separator in tagstring:
            if valid_tag(tagstring):
                tags.append(tagstring)
        else:
            tag_list = [tag.strip() for tag in tagstring.split(separator) if tag]
            for tag in tag_list:
                if valid_tag(tag):
                    tags.append(tag)

    return tags


def edit_string_for_tags(tags):
    names = [tag.name.capitalize() for tag in tags]
    names.sort()
    return ', '.join(names)


def edit_string_for_tag_names(names):
    return ', '.join([name.capitalize() for name in names])


def slugify(tag):
    return tag.replace(' ', '_')
