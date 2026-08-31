/**
 * Was am Download still schiefgeht.
 *
 * Geprueft wird, was niemand sieht, bevor jemand das Archiv entpackt: welche
 * Namen darin stehen, ob gescheiterte Dateien in `_errors.txt` landen statt im
 * Archiv, und ob zwei gleich heissende Dateien einander ueberschreiben.
 */

import JSZip from 'jszip'
import { describe, expect, it, vi } from 'vitest'
import {
  ARCHIVE_FILENAME,
  ERROR_FILENAME,
  UNKNOWN_ERROR,
  buildArchive,
  downloadArchive,
  downloadMarkdown,
  hasResult,
  markdownFilename,
  sanitizeFilename,
  type DownloadEntry,
} from '../download'

function ok(filename: string, markdown = `# ${filename}`): DownloadEntry {
  return { filename, status: 'ok', markdown, error: null }
}

function failed(filename: string, error: string | null = 'Kaputt.'): DownloadEntry {
  return { filename, status: 'failed', markdown: null, error }
}

async function read(blob: Blob): Promise<JSZip> {
  return JSZip.loadAsync(await blob.arrayBuffer())
}

function names(zip: JSZip): string[] {
  return Object.keys(zip.files).sort()
}

describe('sanitizeFilename', () => {
  it.each([
    ['bericht.pdf', 'bericht.pdf'],
    ['../../etc/passwd', 'passwd'],
    ['C:\\Ordner\\bericht.pdf', 'bericht.pdf'],
    ['  bericht.pdf  ', 'bericht.pdf'],
    ['', 'upload'],
    ['.', 'upload'],
    ['..', 'upload'],
    ['/', 'upload'],
  ])('macht aus %j den Namen %j', (given, expected) => {
    expect(sanitizeFilename(given)).toBe(expected)
  })

  it('nimmt auch null und undefined an', () => {
    expect(sanitizeFilename(null)).toBe('upload')
    expect(sanitizeFilename(undefined)).toBe('upload')
  })

  it('wirft Steuerzeichen weg', () => {
    expect(sanitizeFilename(`beri\u0000cht\u001f.pdf`)).toBe('bericht.pdf')
  })

  it('kuerzt von vorn, damit die Endung bleibt', () => {
    const long = `${'a'.repeat(400)}.pdf`
    const result = sanitizeFilename(long)
    expect(result).toHaveLength(255)
    expect(result.endsWith('.pdf')).toBe(true)
  })
})

describe('markdownFilename', () => {
  it.each([
    ['bericht.pdf', 'bericht.md'],
    ['bericht.tar.gz', 'bericht.tar.md'],
    ['ohne-endung', 'ohne-endung.md'],
    ['../../etc/passwd', 'passwd.md'],
    ['.gitignore', '.gitignore.md'],
  ])('macht aus %j die Datei %j', (given, expected) => {
    expect(markdownFilename(given)).toBe(expected)
  })
})

describe('hasResult', () => {
  it('gilt nur fuer fertige Eintraege mit Markdown', () => {
    expect(hasResult(ok('a.pdf'))).toBe(true)
    expect(hasResult(failed('b.pdf'))).toBe(false)
    expect(hasResult({ filename: 'c.pdf', status: 'ok', markdown: null, error: null })).toBe(false)
    expect(hasResult({ filename: 'd.pdf', status: 'queued', markdown: null, error: null })).toBe(
      false,
    )
  })
})

describe('buildArchive', () => {
  it('packt vier Ergebnisse und eine _errors.txt, wenn eine von fuenf scheitert', async () => {
    const entries = [
      ok('a.pdf', '# A'),
      ok('b.docx', '# B'),
      failed('c.epub', 'pandoc: beschaedigtes Archiv'),
      ok('d.pptx', '# D'),
      ok('e.xlsx', '# E'),
    ]

    const zip = await read(await buildArchive(entries))

    expect(names(zip)).toEqual(['_errors.txt', 'a.md', 'b.md', 'd.md', 'e.md'])
    expect(await zip.file('a.md')!.async('string')).toBe('# A')
    expect(await zip.file(ERROR_FILENAME)!.async('string')).toBe(
      'c.epub: pandoc: beschaedigtes Archiv\n',
    )
  })

  it('laesst _errors.txt weg, wenn nichts scheiterte', async () => {
    const zip = await read(await buildArchive([ok('a.pdf'), ok('b.pdf')]))
    expect(names(zip)).toEqual(['a.md', 'b.md'])
  })

  it('nummeriert gleiche Namen durch', async () => {
    const zip = await read(
      await buildArchive([
        ok('bericht.pdf', 'erster'),
        ok('bericht.docx', 'zweiter'),
        ok('bericht.epub', 'dritter'),
      ]),
    )

    expect(names(zip)).toEqual(['bericht-2.md', 'bericht-3.md', 'bericht.md'])
    expect(await zip.file('bericht.md')!.async('string')).toBe('erster')
    expect(await zip.file('bericht-2.md')!.async('string')).toBe('zweiter')
    expect(await zip.file('bericht-3.md')!.async('string')).toBe('dritter')
  })

  it('nennt jede gescheiterte Datei mit einer eigenen Zeile', async () => {
    const zip = await read(await buildArchive([failed('a.pdf', 'kaputt'), failed('b.pdf', null)]))

    expect(names(zip)).toEqual([ERROR_FILENAME])
    expect(await zip.file(ERROR_FILENAME)!.async('string')).toBe(
      `a.pdf: kaputt\nb.pdf: ${UNKNOWN_ERROR}\n`,
    )
  })

  it('haelt Pfadanteile aus dem Archiv heraus', async () => {
    const zip = await read(
      await buildArchive([ok('../../etc/passwd', 'x'), failed('..\\..\\boot.ini', 'kaputt')]),
    )

    expect(names(zip)).toEqual(['_errors.txt', 'passwd.md'])
    expect(await zip.file(ERROR_FILENAME)!.async('string')).toBe('boot.ini: kaputt\n')
  })

  it('nimmt weder Wartende noch Laufende auf — sie sind nicht gescheitert', async () => {
    const zip = await read(
      await buildArchive([
        ok('a.pdf', '# A'),
        { filename: 'b.pdf', status: 'queued', markdown: null, error: null },
        { filename: 'c.pdf', status: 'running', markdown: null, error: null },
      ]),
    )

    expect(names(zip)).toEqual(['a.md'])
  })

  it('baut auch aus nichts ein leeres, lesbares Archiv', async () => {
    const zip = await read(await buildArchive([]))
    expect(names(zip)).toEqual([])
  })
})

describe('downloadMarkdown', () => {
  it('gibt den Rumpf unter dem Namen mit .md weiter', async () => {
    const save = vi.fn()
    downloadMarkdown(ok('bericht.pdf', '# Bericht'), save)

    expect(save).toHaveBeenCalledTimes(1)
    const [blob, filename] = save.mock.calls[0]! as [Blob, string]
    expect(filename).toBe('bericht.md')
    expect(blob.type).toBe('text/markdown;charset=utf-8')
    expect(await blob.text()).toBe('# Bericht')
  })

  it('weigert sich bei einem Eintrag ohne Ergebnis', () => {
    const save = vi.fn()
    expect(() => downloadMarkdown(failed('bericht.pdf'), save)).toThrow(/bericht\.pdf/)
    expect(save).not.toHaveBeenCalled()
  })
})

describe('downloadArchive', () => {
  it('reicht das Archiv unter dem Standardnamen weiter', async () => {
    const save = vi.fn()
    await downloadArchive([ok('a.pdf'), failed('b.pdf')], undefined, save)

    const [blob, filename] = save.mock.calls[0]! as [Blob, string]
    expect(filename).toBe(ARCHIVE_FILENAME)
    expect(blob.type).toBe('application/zip')
    expect(names(await read(blob))).toEqual(['_errors.txt', 'a.md'])
  })

  it('nimmt einen eigenen Namen an', async () => {
    const save = vi.fn()
    await downloadArchive([ok('a.pdf')], 'eigener-name.zip', save)
    expect(save.mock.calls[0]![1]).toBe('eigener-name.zip')
  })
})
