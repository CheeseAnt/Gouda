import { useCallback, useEffect, useState } from "react";
import { getUserCountryEnabledEvents } from "../api";
import { Loader } from "./Loader";
import Event from "./Event";

const useEvents = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(false);
    const [done, setDone] = useState(false);

    // TODO: Make filter for artist, venue, date, price
    // const artists = new Set(events.map(event => event.artists.split(",")).flat())

    const getEvents = useCallback(async () => {
        if(loading) {
            return;
        }
        setLoading(true);
        const res = await getUserCountryEnabledEvents();

        if(!res.ok) {
            setLoading(false);
            setDone(true);
            console.log("Failed to fetch user artists", res)
            return;
        }

        const json = await res.json();
        json.forEach((event) => {
            event['event_details'] = JSON.parse(event['event_details']);
            event['start_date'] = new Date(event['start']);
        })
        // json.sort((a, b) => a['start_date'] < b['start_date'] ? -1 : (a['start_date'] > b['start_date'] ? 1 : 0))

        setEvents(json);
        setLoading(false);
        setDone(true);
    }, [loading, setEvents, setLoading, setDone]);


    useEffect(() => {
        if(events.length || done) {
            return;
        }
        getEvents()
    }, [getEvents, events, done]);

    return { events, loading, refreshEvents: getEvents };
}

const TargettedEvents = () => {
    const { events, loading, refreshEvents } = useEvents();

    return <div>
        {
            loading ? <Loader /> :
            <div className='container'>
                <button className='btn btn-info px-10 w-100' onClick={refreshEvents}>Refresh Events</button>
                <div className="d-flex">
                </div>
                <h4 className="text-muted">Total Events: {events.length}</h4>
                <div className="container">
                    {events.map((event, idx) => {
                        return <Event key={idx} eventData={event} />
                    })}
                </div>
            </div>
        }
    </div>
}

export {TargettedEvents};
