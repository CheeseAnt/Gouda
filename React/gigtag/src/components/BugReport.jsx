import React, { useState } from 'react';
import Button from '@mui/material/Button';
import { BugReport } from '@mui/icons-material';
import { Modal, Form, InputGroup } from 'react-bootstrap';
import { submitBugReport } from '../api';

const BugReportButton = () => {
    const [show, setShow] = useState(false);
    const [bugText, setBugText] = useState("");
    const handleClick = () => {
        setShow(true);
    };

    const submit = () => {
        setShow(false);

        if(!bugText.length) {
            return;
        }

        submitBugReport(bugText);
        setBugText("");
    };

    return (<div>
        <Modal show={show} fullscreen={'xl-down'} onHide={() => setShow(false)}>
            <Modal.Header closeButton>
                <Modal.Title>Submit a Bug</Modal.Title>
            </Modal.Header>
            <Modal.Body className='text-end'>
                <InputGroup className='my-1'>
                    <Form.Group className="mb-3 w-100">
                        <Form.Control autoFocus={true} onChange={(event) => {setBugText(event.target.value)}} style={{resize: 'none'}} as="textarea" rows={4} placeholder='Please write a description of what happened or what you saw in as much detail as you can. Include some steps if possible!'/>
                    </Form.Group>
                </InputGroup>
                <Button variant='outlined' onClick={submit}>Submit</Button>
            </Modal.Body>
        </Modal>
        <Button className="btn report-bug-btn" onClick={handleClick} startIcon={<BugReport />}>
        Report Bug
        </Button>
        </div>
    );
    };

export default BugReportButton;
