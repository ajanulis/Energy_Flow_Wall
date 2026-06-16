#!/usr/bin/env python3
"""
Download all EFW Device datasheets / reference manuals into
/Users/Shared/Projects/EFW/Device/Docs/{01_MCU,02_Display_Touch,03_Sensors,04_Power,05_Mesh,06_Misc}

Idempotent: if a file already exists with non-zero size + PDF header, skip it.
Vendor-original filenames are also recognised via per-entry match_keywords
(e.g. user-downloaded `stm32u585ci.pdf` satisfies the STM32U585 datasheet entry).
Migrates any prior files from ~/Desktop/EFW_Device_HW_Refs into the new layout.

Direct downloads: TI, Sensirion, Diodes Inc → reliable.
Manual downloads: ST (CDN fights curl), Infineon (gated), Goodix, GoodDisplay,
NeoCortec, Nordic, Lite-On → script writes URLs into DOWNLOADS_TODO.md.
"""
from __future__ import annotations
import os, shutil, subprocess, sys
from pathlib import Path
from collections import defaultdict

DOCS_ROOT = Path('/Users/Shared/Projects/EFW/Device/Docs')
OLD_ROOT  = Path(os.path.expanduser('~/Desktop/EFW_Device_HW_Refs'))
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'

# (subfolder, filename, url_or_None, manual_url_or_note, [match_keywords])
# match_keywords: substrings (case-insensitive) — if any *.pdf in the folder
# contains one, the entry counts as present even with a vendor-original name.
MANIFEST = [
    # ─── 01_MCU ───
    ('01_MCU', 'STM32U585xx_datasheet.pdf', None,
        'https://www.st.com/resource/en/datasheet/stm32u585ci.pdf',
        ['stm32u585']),
    ('01_MCU', 'RM0456_STM32U5_reference_manual.pdf', None,
        'https://www.st.com/resource/en/reference_manual/rm0456-stm32u5-series-armbased-32bit-mcus-stmicroelectronics.pdf',
        ['rm0456']),
    ('01_MCU', 'PM0264_Cortex-M33_programming_manual.pdf', None,
        'https://www.st.com/resource/en/programming_manual/pm0264-stm32-cortexm33-mcus-programming-manual-stmicroelectronics.pdf',
        ['pm0264']),
    ('01_MCU', 'ES0499_STM32U585_errata.pdf', None,
        'https://www.st.com/resource/en/errata_sheet/es0499-stm32u575u585-device-errata-stmicroelectronics.pdf',
        ['es0499']),
    ('01_MCU', 'UM2861_NUCLEO-U575ZI-Q_user_manual.pdf', None,
        'https://www.st.com/resource/en/user_manual/um2861-stm32u5-nucleo144-board-mb1549-stmicroelectronics.pdf',
        ['um2861', 'nucleo-u575']),
    ('01_MCU', 'UM2910_STLINK-V3MINIE_user_manual.pdf', None,
        'https://www.st.com/resource/en/user_manual/um2910-stlinkv3mini-debuggerprogrammer-for-stm32-microcontrollers-stmicroelectronics.pdf',
        ['um2910', 'stlinkv3']),

    # ─── 02_Display_Touch ───
    ('02_Display_Touch', 'GDEY042T81-T02_specification.pdf', None,
        'https://www.good-display.com/product/473.html → Downloads → Specification.',
        ['gdey042t81-t02', 'gdey042t81_t02']),  # exclude the -drawing.pdf alias
    ('02_Display_Touch', 'SSD1683_controller_datasheet.pdf', None,
        'Often embedded in the GoodDisplay panel spec PDF; if not, search "SSD1683 datasheet PDF".',
        ['ssd1683']),
    ('02_Display_Touch', 'FT6336U_touch_controller_datasheet.pdf', None,
        'https://www.good-display.com/product/473.html → Downloads → IC Driver FT6336U Datasheet.',
        ['ft6336']),
    ('02_Display_Touch', 'TPS65186_datasheet.pdf',
        'https://www.ti.com/lit/ds/symlink/tps65186.pdf', None,
        ['tps65186']),

    # ─── 03_Sensors ───
    ('03_Sensors', 'SCD4x_datasheet.pdf',
        'https://sensirion.com/media/documents/48C4B7FB/67FE0194/CD_DS_SCD4x_Datasheet_D1.pdf', None,
        ['scd4x_datasheet', 'scd4x_data', 'cd_ds_scd4x']),
    ('03_Sensors', 'SCD4x_low_power_app_note.pdf',
        'https://sensirion.com/media/documents/077BC86F/62BF01B9/CD_AN_SCD4x_Low_Power_Operation_D1.pdf', None,
        ['scd4x_low_power', 'scd4x_lp', 'cd_an_scd4x']),
    ('03_Sensors', 'SHT4x_datasheet.pdf',
        'https://sensirion.com/media/documents/33FD6951/6555C40E/Sensirion_Datasheet_SHT4x.pdf', None,
        ['sht4x', 'sht45']),
    ('03_Sensors', 'BGT60LTR11AIP_datasheet.pdf', None,
        'https://www.infineon.com/cms/en/product/sensor/radar-sensors/radar-sensors-for-iot/60ghz-radar/bgt60ltr11aip/ → Documents.',
        ['bgt60ltr11']),
    ('03_Sensors', 'BGT60LTR11AIP_app_note_autonomous_mode.pdf', None,
        'Same Infineon page → Application Notes → autonomous mode AN. Priority for our use case.',
        ['autonomous_mode', 'bgt60ltr11_an', 'bgt60ltr11s_an']),

    # ─── 04_Power ───
    ('04_Power', 'BQ51013B_datasheet.pdf',
        'https://www.ti.com/lit/ds/symlink/bq51013b.pdf', None,
        ['bq51013b_datasheet', 'bq51013b_data']),
    ('04_Power', 'BQ51013B_design_considerations.pdf',
        'https://www.ti.com/lit/an/slua649b/slua649b.pdf', None,
        ['bq51013b_design', 'slua649']),
    ('04_Power', 'BQ25570_datasheet.pdf',
        'https://www.ti.com/lit/ds/symlink/bq25570.pdf', None,
        ['bq25570']),
    ('04_Power', 'LFP143060_spec.pdf', None,
        'Vendor (lithium-lifepo4-battery.com) will email the spec with the sample order.',
        ['lfp143060', 'lfp_143060']),

    # ─── 05_Mesh ───
    ('05_Mesh', 'NC1000_datasheet.pdf', None,
        'Copy from your existing NeoCortec docs folder (already in hand from Actuator work).',
        ['nc1000']),
    ('05_Mesh', 'NeoCortec_AAPI_specification.pdf', None,
        'Copy from your existing NeoCortec docs folder (AAPI spec + NcApi.c source already in hand).',
        ['aapi', 'neocortec']),

    # ─── 06_Misc ───
    ('06_Misc', 'Nordic_PPK2_user_guide.pdf', None,
        'https://docs.nordicsemi.com/bundle/ug_ppk2/ → Save as PDF from browser. Nordic deprecated direct PDF downloads.',
        ['ppk2']),
    ('06_Misc', 'LTV-356T_optocoupler.pdf', None,
        'Search "LTV-356T datasheet PDF" — Lite-On part. Alternative: PC817 (Sharp) at https://www.farnell.com/datasheets/73758.pdf.',
        ['ltv-356', 'ltv356', 'pc817']),
    ('06_Misc', 'DMG2305UX_N-MOSFET.pdf',
        'https://www.diodes.com/assets/Datasheets/DMG2305UX.pdf', None,
        ['dmg2305']),
]


def is_valid_pdf(p: Path) -> bool:
    if not p.exists() or p.stat().st_size < 1024:
        return False
    with open(p, 'rb') as f:
        return f.read(5) == b'%PDF-'


def find_present(folder: Path, fname: str, keywords: list[str]) -> Path | None:
    """Return the actual file if a matching PDF is present, else None.
       First check the exact expected filename, then fall back to keyword
       substring match against every PDF in the folder."""
    exact = folder / fname
    if is_valid_pdf(exact):
        return exact
    if not folder.exists():
        return None
    for pdf in folder.glob('*.pdf'):
        name_lower = pdf.name.lower()
        if any(kw.lower() in name_lower for kw in keywords):
            if is_valid_pdf(pdf):
                return pdf
    return None


def download(url: str, dest: Path) -> tuple[bool, str]:
    if is_valid_pdf(dest):
        return True, 'already-present'
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ['curl', '-sSL', '--http1.1', '--max-time', '45', '-A', UA, '-o', str(dest), url],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        dest.unlink(missing_ok=True)
        return False, f'curl-error: {r.stderr.strip()[:120] or "timeout"}'
    if not is_valid_pdf(dest):
        size = dest.stat().st_size if dest.exists() else 0
        dest.unlink(missing_ok=True)
        return False, f'not-a-pdf (got {size} bytes — likely HTML redirect)'
    return True, f'{dest.stat().st_size // 1024} KB'


def migrate_old_files():
    if not OLD_ROOT.exists():
        return 0
    rename = {
        'MCU': '01_MCU', 'Devboard': '01_MCU',
        'Display': '02_Display_Touch',
        'Sensors': '03_Sensors',
        'Power': '04_Power',
        'Mesh': '05_Mesh',
        'Programmer': '01_MCU',
        'Misc': '06_Misc',
    }
    moved = 0
    for pdf in OLD_ROOT.rglob('*.pdf'):
        rel = pdf.relative_to(OLD_ROOT)
        old_sub = rel.parts[0] if len(rel.parts) > 1 else 'Misc'
        new_sub = rename.get(old_sub, '06_Misc')
        new_dest = DOCS_ROOT / new_sub / pdf.name
        if not new_dest.exists():
            new_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(pdf), str(new_dest))
            moved += 1
            print(f'  migrated  {pdf.name}  →  {new_sub}/', flush=True)
    for txt in OLD_ROOT.rglob('*.MANUAL.txt'):
        txt.unlink()
    for d in sorted(OLD_ROOT.rglob('*'), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
    if OLD_ROOT.exists() and not any(OLD_ROOT.iterdir()):
        OLD_ROOT.rmdir()
    return moved


def write_todo(by_folder: dict[str, list[tuple[str, str]]]):
    top = DOCS_ROOT / 'DOWNLOADS_TODO.md'
    if not by_folder:
        top.write_text('# EFW Device — Documents Still To Download Manually\n\n'
                       '*All known datasheets are present.* 🎉\n\n'
                       'Re-run `grab_datasheets.py` if you add new entries to the MANIFEST.\n')
        return
    lines = ['# EFW Device — Documents Still To Download Manually',
             '',
             'Generated by `grab_datasheets.py`. Direct downloads completed by the script are in their respective subfolders.',
             '',
             'Click the URLs below in a browser — most fail under curl because of CDN protection (ST), gated downloads (Infineon, Nordic), or login walls.',
             '']
    for folder in sorted(by_folder):
        entries = by_folder[folder]
        lines.append(f'## {folder}')
        lines.append('')
        for fname, note in entries:
            lines.append(f'- **{fname}**')
            for line in note.split('\n'):
                lines.append(f'  {line}')
            lines.append('')
    top.write_text('\n'.join(lines))


def main():
    print(f'Target dir: {DOCS_ROOT}', flush=True)
    DOCS_ROOT.mkdir(parents=True, exist_ok=True)

    if OLD_ROOT.exists():
        print(f'Migrating from old location {OLD_ROOT}…', flush=True)
        n = migrate_old_files()
        print(f'  migrated {n} file(s)', flush=True)

    print()
    print('── Inventory + downloads ──', flush=True)
    fetched, present_exact, present_alias, failed = [], [], [], []
    todo_by_folder: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for subdir, fname, url, manual_url, keywords in MANIFEST:
        folder = DOCS_ROOT / subdir
        found = find_present(folder, fname, keywords)
        if found is not None:
            if found.name == fname:
                present_exact.append((subdir, fname))
                print(f'  PRESENT  {subdir}/{fname}', flush=True)
            else:
                present_alias.append((subdir, found.name))
                print(f'  ALIAS    {subdir}/{found.name}  (covers {fname})', flush=True)
            continue
        if url is None:
            todo_by_folder[subdir].append((fname, manual_url))
            print(f'  MANUAL   {subdir}/{fname}', flush=True)
            continue
        ok, msg = download(url, folder / fname)
        if ok:
            fetched.append((subdir, fname))
            print(f'  FETCHED  {subdir}/{fname}  ({msg})', flush=True)
        else:
            failed.append((subdir, fname, msg))
            todo_by_folder[subdir].append((fname, f'AUTO-DOWNLOAD FAILED ({msg}). Manual URL above.'))
            print(f'  FAIL     {subdir}/{fname}  — {msg}', flush=True)

    write_todo(todo_by_folder)

    print()
    print('── Summary ──')
    print(f'  present (exact name):   {len(present_exact)}')
    print(f'  present (alias name):   {len(present_alias)}')
    print(f'  fetched this run:       {len(fetched)}')
    print(f'  auto-fetch failed:      {len(failed)}')
    print(f'  manual queue:           {sum(len(v) for v in todo_by_folder.values())}')
    print()
    print(f'DOWNLOADS_TODO.md written.')


if __name__ == '__main__':
    main()
