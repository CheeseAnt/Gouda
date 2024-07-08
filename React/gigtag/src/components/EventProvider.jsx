import { useCallback, useEffect, useState } from "react";
import { getUserCountryEnabledEvents } from "../api";
import { EventContext } from "./EventContext";

const useEvents = (setDisplayedEvents) => {
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
        setDisplayedEvents(json);
        setLoading(false);
        setDone(true);
    }, [loading, setEvents, setLoading, setDone, setDisplayedEvents]);


    useEffect(() => {
        if(events.length || done) {
            return;
        }
        getEvents()
    }, [getEvents, events, done]);

    return { events, loading, refreshEvents: getEvents };
}

export const EventProvider = ({children}) => {
    const [displayedEvents, setDisplayedEvents] = useState([]);
    const { events, loading } = useEvents(setDisplayedEvents);

    const provided = {
        events,
        loading,
        displayedEvents,
        setDisplayedEvents,
    };

    return <EventContext.Provider value={provided}>
        {children}
    </EventContext.Provider>
}
