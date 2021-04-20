def get_text_dimensions(text: str, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = max(font.getmask(line).getbbox()[2] for line in text.split('\n') if line)
    text_height = sum(font.getmask(line).getbbox()[3] + descent for line in text.split('\n') if line)

    return text_width, text_height


def split_text(text: str, line_length: int) -> str:
    """
    :param text: The text to split. Keeps original line breaks.
    If impossible to break words in a line, it will remain as is.
    :param line_length: The max line length. Must be higher than 1.
    :return: The message, split over multiple lines to keep within line_length, where possible.
    """
    # The resulting lines.
    result = list()

    lines = text.split('\n')
    for i, line in enumerate(lines):

        # Short lines are not split.
        if len(line) <= line_length:
            result.append(line)
            continue

        # Lines that are long but are all whitespaces are shortened to an empty line.
        if line.isspace():
            result.append('')
            continue

        # Longer lines are split.
        words = line.split(' ')
        new_line = words[0]
        for w in words[1::]:
            # Can't add next word? Break line.
            if len(new_line) + len(w) + 1 > line_length:
                result.append(new_line)
                new_line = w
            # Can add? Add.
            else:
                new_line += ' ' + w
        # Last line.
        result.append(new_line)

    return '\n'.join(result)
