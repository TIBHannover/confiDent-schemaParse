from schemaparse import app
from argparse import ArgumentParser

schemas = ['DataCite', 'CrossRef']
parser = ArgumentParser(description='Test app')
parser.add_argument('-s', '--schema',
                    choices=schemas,
                    default='DataCite',
                    help="Schema which will be turned into MW template")
parser.add_argument('-l', '--list', action='store_true',
                    help="list available schemas")
args = parser.parse_args()


if __name__ == '__main__':
    if args.list:
        print('**Schemas available:**')
        print('\n'.join(schemas))
    else:
        output = app.schema2mw(args.schema)
        print(output)
