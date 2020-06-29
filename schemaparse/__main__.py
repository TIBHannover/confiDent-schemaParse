from schemaparse import app
from schemaparse.utilities import io
from argparse import ArgumentParser

schemas = ['DataCite']  # 'CrossRef'
parser = ArgumentParser(description='Test app')
parser.add_argument('-s', '--schema',
                    choices=schemas,
                    default='DataCite',
                    help="Schema which will be turned into MW template")
parser.add_argument('-l', '--list', action='store_true',
                    help="list available schemas")
parser.add_argument('-o', '--output',
                    help="Filename for output file. "
                         "By default output is printed to console."
                         "Include -o fileme.txt to have file saved to file")
args = parser.parse_args()


if __name__ == '__main__':
    if args.list:
        print('**Schemas available:**')
        print('\n'.join(schemas))
    else:
        output = app.schema2mw(args.schema)
        if not args.output:
            print(output)
        else:
            io.write2file(fn=args.output,
                          content=output)
