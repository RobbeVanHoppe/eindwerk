def test_passing():
    assert 1 == 1


def test_failing():
    # example code voor de stacktrace
    assert 5 == 10


def test_attachment(rp_logger):
    rp_logger.info("Voorbeeld Attachment")

    # Message with an attachment.
    import subprocess
    attachment = subprocess.check_output("nvidia-smi")
    rp_logger.info(
        "Attachment voorbeeld",
        attachment={
            "name": "attachment.txt",
            "data": attachment,
            "mime": "application/octet-stream",
        },
    )
