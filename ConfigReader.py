#!/usr/bin/env python

class Section:
    def has_item(self, item):
        return hasattr(self, item)

    def __getitem__(self, item):
        return self.__dict__[item]

class ConfigReader(object):
    """
    ConfgiReader - An improved config parser.
    """
    def __init__(self):
        self.sections = []

    def __load(self, lines):
        for line in filter(None, lines):
            if line.startswith("["):
                cursec = line.split("[")[-1].split("]")[0]
                self.sections.append(cursec)
                section = Section()
                setattr(self, cursec, section)
            elif line.startswith(";") or line.startswith("#"):
                next
            else:
                x = line.split("=")
                if len(x) > 1:
                    delim = "="
                else:
                    x = line.split(":")
                    delim = ":"
                key = x[0]
                value = delim.join(x[1:])
                setattr(section, key.strip(), value.strip() % section)

    def read(self, cfg):
        """
        read(configfile) -> This loads a configfile into the object
        """
        try:
            f = open(cfg, 'rb')
            self.__load(map(lambda x: x.strip(), f.readlines()))
            f.close()
        except IOError:
            raise StandardError("Couldn't find config file: %s" % (cfg))

    def get_sections(self):
        """
        get_sections() -> Returns a list of the sections from the loaded config file.
        """
        return self.sections

    def has_section(self, section='DEFAULT'):
        """
        has_section(section_name) -> Returns a boolean for the presence of a section.
        If no section name is passed, it defaults to 'DEFAULT' as the section name.
        """
        return section.strip() in self.sections

    def get_items(self, section='DEFAULT'):
        """
        get_items(section_name) -> Returns the dictionary of items found with in the 
        specified section.  If no section name is passed, it defaults to 'DEFAULT' as 
        the section name.
        """
        return self.__dict__[section].__dict__

    def __getitem__(self, item):
        return self.__dict__[item]

if __name__ == "__main__":
    C = ConfigReader()
    #C.read("test.cfg")
    #print(C.get_items('TYPES'))
    #print(C.debug.level)

    C.read("OMQS.cfg")
    print(C.Global.MQURL)
    print (C.debug.level)
#    print(C.DEFAULT.name)
#    print(C.get_sections())
#    print(C.DEFAULT['fname'])
#    print(C.testnames.t2)
#    print(C.get_items('test'))
#    print(C.test[';this'])
#    print(C.test.this)
#    print(C.DEFAULT.fname)
#    print(C['DEFAULT'].fname)
#    print(C['DEFAULT']['fname'])
#    defs = C.DEFAULT
#    print(getattr(defs, 'lname'))
