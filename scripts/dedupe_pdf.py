# -*- coding: utf-8 -*-
"""Collapse duplicate streams in a PDF.

Chrome rasterises each card shadow per page. With 372 identical daily
pages that means thousands of byte-identical images, and the file balloons
(494 pages measured at 86MB, of which 52MB was duplicated images).

This hashes every stream object, keeps one copy of each, and repoints the
rest at it.
"""

import hashlib
import os
import sys

import pikepdf


def dedupe(src, dst):
    pdf = pikepdf.open(src)
    first = {}          # digest -> the object we keep
    replace = {}        # objgen of a duplicate -> the kept object

    for obj in pdf.objects:
        if not isinstance(obj, pikepdf.Stream):
            continue
        try:
            raw = obj.read_raw_bytes()
        except Exception:
            continue
        # include the stream dict so we never merge streams that decode
        # differently but happen to share bytes
        meta = repr(sorted(
            (str(k), str(v)) for k, v in obj.items() if k != "/Length"))
        digest = hashlib.sha256(raw + meta.encode()).hexdigest()
        if digest in first:
            replace[obj.objgen] = first[digest]
        else:
            first[digest] = obj

    def repoint(node):
        """Swap direct children that point at a duplicate. No recursion --
        pdf.objects already enumerates every indirect object."""
        if isinstance(node, pikepdf.Dictionary):
            for k in list(node.keys()):
                v = node[k]
                if getattr(v, "is_indirect", False) and v.objgen in replace:
                    node[k] = replace[v.objgen]
        elif isinstance(node, pikepdf.Array):
            for i in range(len(node)):
                v = node[i]
                if getattr(v, "is_indirect", False) and v.objgen in replace:
                    node[i] = replace[v.objgen]

    # Folding duplicate pattern/shading dictionaries was tried and dropped.
    # It folded 5,328 of them and the file came out byte for byte the same
    # size -- they are tiny and the object streams already compress the
    # repetition away. Measure before keeping a pass like that.

    for obj in pdf.objects:
        if isinstance(obj, pikepdf.Stream):
            repoint(obj.stream_dict)
        else:
            repoint(obj)
    repoint(pdf.Root)

    # The accessibility tag tree stays. Chrome writes 33,710 StructElem
    # objects here, 753,508 bytes, 3.7% of the file, and stripping them was
    # tried on 2026-09-23 to make room for twenty Notes pages. The user chose
    # to keep them and ship eight Notes pages instead: without tags a screen
    # reader loses heading navigation, and a planner for ADHD readers is not
    # the place to spend that. Reading order and text extraction survive
    # either way -- it is the jump-to-heading list that goes.

    pdf.save(dst, object_stream_mode=pikepdf.ObjectStreamMode.generate,
             compress_streams=True, linearize=False)
    pdf.close()
    return len(replace), len(first)


if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src.replace(".pdf", "_slim.pdf")
    before = os.path.getsize(src)
    dropped, kept = dedupe(src, dst)
    after = os.path.getsize(dst)
    print(f"{dropped} duplicate streams folded into {kept} unique")
    print(f"{before/1048576:.1f} MB -> {after/1048576:.1f} MB "
          f"({100 * (1 - after / before):.0f}% smaller)")
