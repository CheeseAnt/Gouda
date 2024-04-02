import { useCallback, useEffect, useState } from 'react';
import Modal from 'react-bootstrap/Modal';
import { getArtistEvents } from '../api';
import { Loader } from './Loader';
import { Button } from 'react-bootstrap';
import Event from './Event';

const ArtistEvents = ({artist, show, setShow}) => {
    const [loading, setLoading] = useState(false);
    const [done, setDone] = useState(false);
    const [events, setEvents] = useState([]);

    const getEvents = useCallback(async (refresh=false) => {
        setLoading(true);
        const res = await getArtistEvents(artist.name, refresh);

        if(!res.ok) {
            console.log("Failed to get artist events", res);
            setLoading(false);
            setDone(true);
            return
        }

        setEvents(await res.json());

        setDone(true);
        setLoading(false);
    }, [artist.name, setLoading, setDone, setEvents]);

    useEffect(() => {
        if(!show || events.length || loading || !Object.keys(artist).length || done) {
            return;
        }

        getEvents();
    }, [events, loading, artist, done, show, getEvents])

    const close = () => {
        setShow(false);
        setDone(false);
        setEvents([]);
    }

    return (    
        <Modal className='modal-lg' show={show} fullscreen={'xl-down'} onHide={close}>
            <Modal.Header closeButton>
                <Modal.Title>{artist.name}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                { loading ? <Loader /> :
                <div>
                    <Button className='btn gg-cream gg-cream-o w-100' onClick={() => getEvents(true)}>Refresh</Button>
                    {
                        done && events.length === 0 ? <h2>No Events Found</h2> : 
                        events.map((event, idx) => {
                            return <Event key={idx} eventData={event} />
                        })
                    }
                </div>
                }
            </Modal.Body>
        </Modal>
    );
}

export default ArtistEvents;