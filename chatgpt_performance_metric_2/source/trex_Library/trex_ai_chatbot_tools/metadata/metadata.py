from ..parser.mdBlock import mdType, mdBlock
from ..chunker.datacell import DataCell


def get_metadata(chunks: list[DataCell]) -> None:
    get_index_data(chunks)
    for chunk in chunks:
        convert_image_data(chunk)


def get_index_data(cell_list: list[DataCell]) -> None:
    section_count = {}
    for cell in cell_list:
        section_list = cell.section
        for i in range(1, len(section_list) + 1):
            try:
                section_count[tuple(section_list[:i])][1] += 1
            except KeyError:
                section_count[tuple(section_list[:i])] = [0, 1]
    for cell in cell_list:
        result = []
        section_list = cell.section
        for i in range(1, len(section_list) + 1):
            result.append(tuple(section_count[tuple(section_list[:i])]))
            section_count[tuple(section_list[:i])][0] += 1
        cell.metadata.update({"sectionIndex": result})


def convert_image_data(chunk: DataCell) -> None:
    def get_imgBlock(root: mdBlock, map: tuple[int], index: int = 0) -> mdBlock:
        if index < len(map):
            return get_imgBlock(root.content[map[index]], map, index + 1)
        return root

    def export_image(block: mdBlock) -> dict:
        return {
            "file_name": block.imgpath.name,
            "alt_text": block.alt,
            "text_path": block.textpath.as_posix(),
            "img_path": block.imgpath.as_posix(),
        }

    img_list = []
    for block in chunk.data:
        if block.type == mdType.Image:
            img_list.append(export_image(block))
            continue
        for index in block.imgIndex:
            img_list.append(export_image(get_imgBlock(block, index)))
    if img_list:
        chunk.metadata.update({"imageData": img_list})
