import { useCallback, useEffect, useState } from "react";
import { getUserCountryEnabledEvents } from "../api";
import { Loader } from "./Loader";

const useEvents = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(false);
    const [done, setDone] = useState(false);

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

        setEvents(await res.json());
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
                {events.map(event => {
                    return <div key={event.event_id + event.attraction_id} className='event d-flex'>
                        {event.id}
                        {event.onsale}
                    </div>
                })}
            </div>
        }
    </div>
}

export {TargettedEvents};
