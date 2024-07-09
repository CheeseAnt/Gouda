import React, { createContext, useContext, useEffect, useCallback, useState, useMemo } from 'react';
import { slide as Menu } from 'react-burger-menu';
import styles from './EventFilter.module.css'
import { FilterListOutlined } from '@mui/icons-material';
import { Button, Checkbox, List, ListItem, ListItemButton, ListItemIcon, ListItemText, ListSubheader, Slider } from '@mui/material';
import { EventContext } from './EventContext';

const FilterContext = createContext({});

const useFilter = (filter) => {
  const { registerFilter, unregisterFilter } = useContext(FilterContext);

  useEffect(() => {
    registerFilter(filter);
    return () => {
      unregisterFilter(filter);
    };
  }, [filter, registerFilter, unregisterFilter]);
};

const FilterProvider = ({children, data, onFilterChange}) => {
  const [filters, setFilters] = useState([]);

  const registerFilter = useCallback((filter) => {
    setFilters((prevFilters) => [...prevFilters, filter]);
  }, []);

  const unregisterFilter = useCallback((filter) => {
    setFilters((prevFilters) => prevFilters.filter(f => f !== filter));
  }, []);

  const applyFilters = useCallback(() => {
    const filteredData = data.filter(dataPoint => {

      for (let index = 0; index < filters.length; index++) {
        const filter = filters[index];
        if(!filter(dataPoint)) {
          return false;
        }
      }
  
      return true;
    });

    onFilterChange(filteredData);
  }, [onFilterChange, data, filters]);

  const provided = {
    registerFilter,
    unregisterFilter,
    applyFilters,
  };

  return <FilterContext.Provider value={provided}>
    {children}
  </FilterContext.Provider>
}

const CheckFilter = ({filters, title, dataKey, condition}) => {
  const [checked, setChecked] = useState({})
  const filteredValues = useMemo(() => Object.keys(checked).filter(key => checked[key]), [checked]);

  const filter = useCallback((dataPoint) => {
    // default to true
    if(!filteredValues.length) {
      return true;
    }

    // filter by the condition otherwise
    const dataValue = dataPoint[dataKey];
    return (condition ?? (() => true))(dataValue, filteredValues);
  }, [filteredValues, dataKey, condition]);

  useFilter(filter);

  useEffect(() => {
    const c = filters.reduce((acc, filter) => {acc[filter] = false; return acc;}, {});
    setChecked(c);
  }, [filters])

  const onChange = (key) => {
    setChecked((prev) => {prev[key] = !prev[key]; return {...prev}});
  }

  return <div className={styles.filterSectionContainer}>
    <ListSubheader className={styles.subtitle}>{title}</ListSubheader>
    <List className={styles.filterSection}>
      {Object.keys(checked).map((key, idx) => {
        return <ListItem key={idx} className={styles.filterItem}>
        <ListItemButton className={styles.filterButton} onClick={() => onChange(key)} dense>
          <ListItemIcon className={styles.filterIcon}>
            <Checkbox
              edge="start"
              checked={checked[key]}
              disableRipple
            />
          </ListItemIcon>
          <ListItemText primary={key} />
        </ListItemButton>
      </ListItem>
      })}
    </List>
  </div>
}

const DateFilter = ({min, max, title, dataKey, condition}) => {
  const [dateRange, setDateRange] = useState([
    min,
    max,
  ]);

  const filter = useCallback((dataPoint) => {
    // default to true
    if(!dateRange) {
      return true;
    }

    // filter by the condition otherwise
    const dataValue = dataPoint[dataKey];
    return (condition ?? (() => true))(dataValue, dateRange);
  }, [dateRange, dataKey, condition]);

  useFilter(filter);

  const onChange = (_, newValue) => {
    setDateRange(newValue)
  };

  const valueLabelFormat = (value) => {
    return new Date(value).toDateString();
  };

  return <div className={styles.filterSectionContainer}>
    <ListSubheader className={styles.subtitle}>{title}</ListSubheader>
    <Slider
      className={styles.dateFilter}
      getAriaLabel={() => title}
      value={dateRange}
      min={min}
      max={max}
      onChange={onChange}
      valueLabelDisplay="auto"
      valueLabelFormat={valueLabelFormat}
    />
  </div>
}

const EventFilter = () => {
  // const [filters, setFilters] = useState({
  //   artist: '',
  //   venue: '',
  //   country: '',
  //   date: '',
  //   price: '',
  // });

  const { loading, events, setDisplayedEvents } = useContext(EventContext);

  const artists = useMemo(() => {
    let artists = [];
    events.forEach(event => {
      event.artists?.split(",").forEach(artist => artists.push(artist))
    })
    artists = [...(new Set(artists))].sort();
    return artists;
  }, [events]);

  const venues = useMemo(() => {
    let venues = events.map(event=>event.venue);
    venues = [...(new Set(venues))].sort();
    return venues;
  }, [events]);

  const [minDate, maxDate] = useMemo(() => {
    let dates = events.map(event=>event.start_date.getTime()).filter(date=>date).sort()
    const minDate = dates[0];
    const maxDate = dates[dates.length-1];

    return [minDate, maxDate];
  }, [events]);


  // const filteredEvents = events.filter((event) => {
  //   const { artistName, venue, country, date, price } = event; // Assuming artist object structure

  //   return (
  //     artistName.toLowerCase().includes(filters.artists.toLowerCase()) &&
  //     venue.toLowerCase().includes(filters.venue.toLowerCase()) &&
  //     country.toLowerCase().includes(filters.country.toLowerCase()) &&
  //     (!filters.date || new Date(date) >= new Date(filters.date)) && // Date filter (optional)
  //     (!filters.price || price <= parseFloat(filters.price)) // Price filter (optional)
  //   );
  // });

  if(loading) return null;

  return <div>
    <FilterProvider data={events} onFilterChange={setDisplayedEvents}>
      <Menu className={`${styles.sideBar}`}
      noOverlay={true} isOpen={true}
      burgerBarClassName={styles.burgerBar}
      burgerButtonClassName={styles.burgerButton}
      menuClassName={styles.burgerMenu}
      customBurgerIcon={<FilterListOutlined />}
      >
        <CheckFilter filters={artists} title='Artist' dataKey='artists' condition={
          (artists, filtered) => (new Set(filtered)).intersection(new Set(artists.split(","))).size
        }/>
        <CheckFilter filters={venues} title='Venue' dataKey='venue' condition={
          (venue, filtered) => filtered.includes(venue)
        }/>
        <DateFilter min={minDate} max={maxDate} title='Date' dataKey='start_date' condition={
          (start, minmax) => (minmax[0] <= start.getTime() && start.getTime() <= minmax[1])
        }/>
        <FilterContext.Consumer>
          {ctx => <Button onClick={ctx.applyFilters} className={`gg-black ${styles.applyButton}`}>Apply</Button>}
        </FilterContext.Consumer>
      </Menu>
    </FilterProvider>
  </div>
};

export default EventFilter;
