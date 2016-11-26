#!/usr/bin/env python3
# coding: utf-8

import argparse
import re
import zipfile

def parse(b):
    soup = bs4.BeautifulSoup(b, features='xml')
    scr = soup.find('script')
    paths, part, cur, style = [], None, None, None
    for l in scr.text.splitlines():
        l = l.strip()
        if not l:
            continue
        if l.startswith('ctx.moveTo'):
            cur = [l]
            part.append(cur)
        elif l.startswith('ctx.lineTo'):
            cur.append(l)
        elif l == 'ctx.fill();':
            part, cur, style = None, None, None
        elif l.startswith('// #path'):
            part, style = [], []
            paths.append((style, part))
        elif l.startswith('ctx.fillStyle'):
            style.append(l.split("'")[1])
        elif cur is not None:
            raise ValueError('Invalid input line: {}'.format(l))
    return paths
        
def gen_csv(paths, outfile):
    le_regex = re.compile(r'ctx.(move|line)To\(([0-9.]+), ([0-9.]+)\);')
    scale = 0.188*1.5
    with zipfile.ZipFile(outfile, 'w') as f:
        for i, (style, parts) in enumerate(paths):
            for j, segments in enumerate(parts):
                parsed = [ le_regex.match(seg).groups()[1:] for seg in segments ]
                f.writestr('curveexport/{:04d}-{:04d}.csv'.format(i, j),
                    '"Index","X (mm)","Y (mm)","Arc Angle (Neg = CW)"\n' +\
                    '\n'.join('"{}","{}","{}",""'.format(i, scale*float(x), scale*float(y)) for i, (x, y) in enumerate(parsed)))
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Altium region-compatible CSV from Inkscape HTML canvas output')
    parser.add_argument('infile', argparse.FileType('rb'))
    parser.add_argument('outfile', argparse.FileType('wb'))

    paths = parse(parser.infile.read())
    gen_csv(paths, parser.outfile)
