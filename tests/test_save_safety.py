import io
from pathlib import Path

import pikepdf
from PIL import Image
import pytest
import PDFtoPDFocr_2 as app


def pdf_bytes(pages=1):
    pdf = pikepdf.Pdf.new()
    for _ in range(pages):
        pdf.add_blank_page(page_size=(100,100))
    buffer = io.BytesIO()
    pdf.save(buffer)
    pdf.close()
    return buffer.getvalue()


def synthetic_pdf(path, pages=1):
    path.write_bytes(pdf_bytes(pages))
    return path


def synthetic_worker(monkeypatch, images=2):
    worker = app.OCRWorker([], 'eng')
    monkeypatch.setattr(worker, '_load_source_images', lambda _: [Image.new('RGB',(10,10),'white') for _ in range(images)])
    return worker


def test_empty_ocr_page_does_not_publish_partial_success(tmp_path, monkeypatch):
    source = synthetic_pdf(tmp_path/'scan.pdf',2)
    output = tmp_path/'scan_ocred.pdf'
    output.write_bytes(b'previous')
    worker = synthetic_worker(monkeypatch)
    results = iter([pdf_bytes(),b''])
    monkeypatch.setattr(app.pytesseract,'image_to_pdf_or_hocr',lambda *a,**kw:next(results))
    assert worker._ocr_pdf(str(source),'eng') is False
    assert output.read_bytes() == b'previous'


def test_incomplete_rasterization_preserves_output(tmp_path, monkeypatch):
    source = synthetic_pdf(tmp_path/'scan.pdf',2)
    output = tmp_path/'scan_ocred.pdf'
    output.write_bytes(b'previous')
    monkeypatch.setattr(app,'convert_from_path',lambda *a,**kw:[Image.new('RGB',(10,10),'white')])
    monkeypatch.setattr(app.pytesseract,'image_to_pdf_or_hocr',lambda *a,**kw:pdf_bytes())
    assert app.OCRWorker([], 'eng')._ocr_pdf(str(source),'eng') is False
    assert output.read_bytes() == b'previous'


@pytest.mark.parametrize('operation',['ocr','merge'])
def test_partial_pdf_write_preserves_previous_output(tmp_path, monkeypatch, operation):
    source = synthetic_pdf(tmp_path/'scan.pdf')
    second = synthetic_pdf(tmp_path/'second.pdf')
    target = tmp_path/('scan_ocred.pdf' if operation=='ocr' else 'merged.pdf')
    target.write_bytes(b'previous')
    original = {p:p.read_bytes() for p in (source,second)}
    worker = synthetic_worker(monkeypatch,1)
    page = pdf_bytes()
    monkeypatch.setattr(app.pytesseract,'image_to_pdf_or_hocr',lambda *a,**kw:page)
    def partial_save(self,destination,*a,**kw):
        Path(destination).write_bytes(b'partial')
        raise OSError('synthetic partial save')
    monkeypatch.setattr(app.pikepdf.Pdf,'save',partial_save)
    if operation=='ocr':
        assert worker._ocr_pdf(str(source),'eng') is False
    else:
        with pytest.raises(OSError,match='partial save'):
            app.merge_ocr_outputs([str(source),str(second)],target.name,tmp_path)
    assert target.read_bytes() == b'previous'
    assert all(p.read_bytes()==old for p,old in original.items())


def test_partial_manifest_write_preserves_previous_output(tmp_path,monkeypatch):
    target = tmp_path/'job.json'
    target.write_bytes(b'previous')
    def partial_write(self,*a,**kw):
        self.write_bytes(b'partial')
        raise OSError('synthetic manifest error')
    monkeypatch.setattr(Path,'write_text',partial_write)
    with pytest.raises(OSError):
        app.write_job_export(target,{'synthetic':'äöü'})
    assert target.read_bytes() == b'previous'


def test_invalid_ocr_pdf_cleans_fallback_temporary_file(tmp_path,monkeypatch):
    source = synthetic_pdf(tmp_path/'source.pdf')
    before = set(tmp_path.iterdir())
    worker = synthetic_worker(monkeypatch,1)
    monkeypatch.setattr(app.pytesseract,'image_to_pdf_or_hocr',lambda *a,**kw:b'invalid PDF bytes')
    monkeypatch.setattr(app.tempfile,'gettempdir',lambda:str(tmp_path))
    assert worker._ocr_pdf(str(source),'eng') is False
    assert set(tmp_path.iterdir()) == before


def test_one_ocr_frame_cannot_add_multiple_pages(tmp_path,monkeypatch):
    source = synthetic_pdf(tmp_path/'scan.pdf')
    target = tmp_path/'scan_ocred.pdf'
    target.write_bytes(b'previous')
    worker = synthetic_worker(monkeypatch,1)
    monkeypatch.setattr(app.pytesseract,'image_to_pdf_or_hocr',lambda *a,**kw:pdf_bytes(2))
    assert worker._ocr_pdf(str(source),'eng') is False
    assert target.read_bytes() == b'previous'


@pytest.mark.parametrize('operation', ['ocr','manifest','merge'])
def test_final_replace_failure_preserves_outputs(tmp_path,monkeypatch,operation):
    source = synthetic_pdf(tmp_path/'scan.pdf')
    second = synthetic_pdf(tmp_path/'second.pdf')
    name = {'ocr':'scan_ocred.pdf','manifest':'job.json','merge':'merged.pdf'}[operation]
    target = tmp_path/name
    target.write_bytes(b'previous')
    before = {p:p.read_bytes() for p in tmp_path.iterdir()}
    worker = synthetic_worker(monkeypatch,1)
    page = pdf_bytes()
    monkeypatch.setattr(app.pytesseract,'image_to_pdf_or_hocr',lambda *a,**kw:page)
    def denied(*args):
        raise PermissionError('synthetic sharing violation')
    monkeypatch.setattr(app.os,'replace',denied)
    if operation == 'ocr':
        assert worker._ocr_pdf(str(source),'eng') is False
    else:
        with pytest.raises(PermissionError):
            if operation == 'manifest':
                app.write_job_export(target,{'synthetic':True})
            else:
                app.merge_ocr_outputs([str(source),str(second)],target.name,tmp_path)
    assert {p for p in tmp_path.iterdir() if p.is_file()} == set(before)
    assert not list(tmp_path.glob('pdftopdfocr-output-*'))
    assert all(p.read_bytes() == old for p,old in before.items())


def test_archive_partial_copy_preserves_individual_pdf(tmp_path,monkeypatch):
    source = synthetic_pdf(tmp_path/'a.pdf')
    second = synthetic_pdf(tmp_path/'b.pdf')
    before = source.read_bytes()
    def partial_copy(source,destination):
        Path(destination).write_bytes(b'partial')
        raise OSError('synthetic archive copy failure')
    monkeypatch.setattr(app.shutil,'copyfile',partial_copy)
    with pytest.raises(app.MergeArchiveError) as error:
        app.merge_ocr_outputs([str(source),str(second)],'merged.pdf',tmp_path)
    assert error.value.merged_path == tmp_path/'merged.pdf'
    with pikepdf.open(error.value.merged_path) as pdf:
        assert len(pdf.pages) == 2
    assert source.read_bytes() == before
    assert second.exists()
    assert not list((tmp_path/app.MERGE_SUBFOLDER_NAME).iterdir())


def test_archive_unlink_failure_reports_saved_pdf_and_keeps_source(tmp_path,monkeypatch):
    source = synthetic_pdf(tmp_path/'a.pdf')
    second = synthetic_pdf(tmp_path/'b.pdf')
    original_unlink = Path.unlink
    def denied(path,*args,**kwargs):
        if path == source:
            raise PermissionError('source held open')
        return original_unlink(path,*args,**kwargs)
    monkeypatch.setattr(Path,'unlink',denied)
    warnings = []
    merged = app.merge_ocr_outputs([str(source),str(second)],'merged.pdf',tmp_path,archive_warnings=warnings)
    assert merged.exists() and source.exists()
    assert warnings and 'source held open' in warnings[0]
    assert (tmp_path/app.MERGE_SUBFOLDER_NAME/source.name).read_bytes() == source.read_bytes()


@pytest.mark.parametrize('alias',['direct','hardlink'])
def test_merge_rejects_input_alias_before_changes(tmp_path,monkeypatch,alias):
    source = synthetic_pdf(tmp_path/'a.pdf')
    second = synthetic_pdf(tmp_path/'b.pdf')
    target = source if alias == 'direct' else tmp_path/'alias.pdf'
    if alias == 'hardlink':
        try:
            target.hardlink_to(source)
        except OSError as error:
            pytest.skip(f'Hardlinks unavailable: {error}')
    before = {p:p.read_bytes() for p in tmp_path.iterdir()}
    with pytest.raises(ValueError,match='Quelldatei'):
        app.merge_ocr_outputs([str(source),str(second)],target.name,tmp_path)
    assert set(tmp_path.iterdir()) == set(before)
    assert all(p.read_bytes() == old for p,old in before.items())


@pytest.mark.parametrize('processing_fails',[False,True])
def test_cleanup_does_not_change_commit_status(tmp_path,monkeypatch,processing_fails):
    target = tmp_path/'job.json'
    target.write_bytes(b'previous')
    original_cleanup = app.tempfile.TemporaryDirectory.cleanup
    def cleanup(directory):
        original_cleanup(directory)
        raise PermissionError('synthetic cleanup denied')
    monkeypatch.setattr(app.tempfile.TemporaryDirectory,'cleanup',cleanup)
    if processing_fails:
        def denied(*args):
            raise PermissionError('primary publish failure')
        monkeypatch.setattr(app.os,'replace',denied)
        with pytest.raises(PermissionError,match='primary publish failure'):
            app.write_job_export(target,{'synthetic':True})
        assert target.read_bytes() == b'previous'
    else:
        assert app.write_job_export(target,{'synthetic':'äöü'}) == target
        assert 'äöü' in target.read_text(encoding='utf-8')


def test_gui_manifest_failure_has_no_success_feedback(tmp_path,monkeypatch):
    from PySide6.QtWidgets import QApplication
    qt = QApplication.instance() or QApplication([])
    gui = app.OCRConverterGUI()
    target = tmp_path/'job.json'
    target.write_bytes(b'previous')
    def denied(*args):
        raise PermissionError('synthetic destination locked')
    feedback = []
    monkeypatch.setattr(app.os,'replace',denied)
    monkeypatch.setattr(app.QMessageBox,'information',lambda *args:feedback.append('success'))
    monkeypatch.setattr(app.QMessageBox,'critical',lambda *args:feedback.append('error'))
    try:
        assert gui.export_job_manifest(target_path=target) is None
        assert feedback == ['error']
        assert 'synthetic destination locked' in gui.status_label.text()
        assert target.read_bytes() == b'previous'
    finally:
        gui.close()
        qt.processEvents()


@pytest.mark.parametrize('operation',['ocr','merge'])
def test_silently_corrupted_written_pdf_is_not_published(tmp_path,monkeypatch,operation):
    source = synthetic_pdf(tmp_path/'scan.pdf')
    second = synthetic_pdf(tmp_path/'second.pdf')
    target = tmp_path/('scan_ocred.pdf' if operation == 'ocr' else 'merged.pdf')
    target.write_bytes(b'previous')
    worker = synthetic_worker(monkeypatch,1)
    page = pdf_bytes()
    monkeypatch.setattr(app.pytesseract,'image_to_pdf_or_hocr',lambda *a,**kw:page)
    def invalid_save(pdf,path,*args,**kwargs):
        Path(path).write_bytes(b'not a valid PDF')
    monkeypatch.setattr(app.pikepdf.Pdf,'save',invalid_save)
    if operation == 'ocr':
        assert worker._ocr_pdf(str(source),'eng') is False
    else:
        with pytest.raises(pikepdf.PdfError):
            app.merge_ocr_outputs([str(source),str(second)],'merged.pdf',tmp_path)
    assert target.read_bytes() == b'previous'
    assert source.exists() and second.exists()
