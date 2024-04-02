import { useCallback, useEffect, useRef, useState } from "react";
import { getUserCountryEnabledEvents } from "../api";
import { Loader } from "./Loader";
import Event from "./Event";

const useNearBottom = () => {
    const [isNearBottom, setIsNearBottom] = useState(false);
    const previous = useRef(false);
    const [trigger, setTrigger] = useState(false);

    const handleScroll = (event) => {
        const { scrollHeight } = document.body;
        const { height } = window.screen;
        const { scrollY } = window;
        const threshold = height; // Adjust threshold value as needed (in pixels)

        const isCloseToBottom = scrollY >= (scrollHeight-height) - threshold;
        setIsNearBottom(isCloseToBottom);
    };

    useEffect(() => {
        window.addEventListener('scroll', handleScroll);

        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }, []);

    useEffect(() => {
        if (isNearBottom && !previous.current) {
            previous.current = true;
            setTrigger(true);
        }
        else if (!isNearBottom && previous.current) {
            previous.current = false;
            setTrigger(false);
        }
    }, [isNearBottom]);

    return {trigger};
}

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
    const { events, loading } = useEvents();
    const [ loadingMore, setLoadingMore ] = useState(true);
    const [ limit, setLimit ] = useState(50)
    const { trigger } = useNearBottom();

    useEffect(() => {
        if(!trigger) {
            return;
        }

        setLimit(previous => {
            if (previous >= events.length) {
                setLoadingMore(false);

                return previous
            };

            setLoadingMore(true);
            return Math.min(previous + 10, events.length)
        });
    }, [trigger, events.length])

    return <div>
        {
            loading ? <Loader /> :
            <div className='container'>
                <div className="d-flex">
                </div>
                <h4 className="text-muted" style={{left: "10%", position: "absolute"}}>Total Events: {events.length}</h4>
                <div className="container">
                    {events.slice(0, limit).map((event, idx) => {
                        return <Event key={idx} eventData={event} />
                    })}
                    {loadingMore ? <Loader /> : null}
                </div>
            </div>
        }
    </div>
}

export {TargettedEvents};
