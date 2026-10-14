import {
  anchor,
  anchorLink,
  blockquote,
  bold,
  button,
  buttonRow,
  code,
  dateTime,
  details,
  doc,
  emoji,
  heading,
  list,
  map,
  marked,
  paragraph,
  photo,
  reference,
  referenceLink,
  sub,
  table,
  userMention,
} from 'tg-rich-messages';

const message = doc(
  heading(1, 'Field report'),
  paragraph([
    bold('Status: '),
    marked('ready'),
    ' — release ',
    code('v2.4'),
    '. ',
    sub('UTC'),
    ' update ',
    dateTime('14:30', 1791988200, 'wDT'),
    '; owner ',
    userMention('@maintainer', 123456789),
    ' ',
    emoji('5368324170671202286', '👍'),
    '.',
  ]),
  anchor('metrics'),
  heading(2, 'Metrics'),
  table(
    [
      [
        { content: 'Measure', header: true },
        { content: 'Result', header: true },
        { content: 'Note', header: true },
      ],
      [
        { content: 'Latency', rowspan: 2, align: 'left', valign: 'middle' },
        { content: '42 ms', align: 'right' },
        { content: 'p50', align: 'center' },
      ],
      [{ content: 'Region', colspan: 2, align: 'center' }],
    ],
    { bordered: true, striped: true, compact: true, caption: 'Measured this morning' },
  ),
  list(
    [
      { content: 'Build verified', checkbox: true, checked: true },
      { content: 'Publish report', checkbox: true },
      { content: 'Notify team', value: 9, type: 'a' },
    ],
    { ordered: true, start: 7, type: '1' },
  ),
  blockquote('Keep the source data attached to every reported value.', 'Operations', {
    expandable: true,
  }),
  details('References', [
    paragraph([
      reference('Measurement protocol', 'protocol'),
      ' — see ',
      referenceLink('protocol note', 'protocol'),
      ' or ',
      anchorLink('the metrics section', 'metrics'),
      '.',
    ]),
  ]),
  photo('https://telegram.org/example/photo.jpg', {
    caption: 'Instrument panel',
    credit: 'Operations',
    spoiler: true,
  }),
  map(41.9, 12.5, 14, { caption: 'Test site', credit: 'Field team' }),
  buttonRow(
    [
      button('Open report', { type: 'url', style: 'primary', url: 'https://example.com/report' }),
      button('Copy reference', { type: 'copy_text', text: 'REPORT-2026-10' }),
    ],
    { align: 'left' },
  ),
);

message.validate();
const payload = message.toInputRichMessage({ isRtl: false, skipEntityDetection: true });
console.log(JSON.stringify(payload, null, 2));
