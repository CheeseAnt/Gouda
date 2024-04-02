import React, { useState } from 'react';
import { Button, Box, Card, CardContent, CardMedia, Divider, Typography, Grid, Chip } from '@mui/material';
import { Container } from 'react-bootstrap';
import { updateEventNotification } from '../api';

const Event = ({ eventData }) => {
    const {
        event_id,
        artists,
        country,
        event_details: {
            name,
            images,
            url,
            dates: { start },
            sales,
            classifications: [primaryClassification],
            priceRanges,
            _embedded: { venues: [venue] },
        },
    } = eventData;

    const [saleN, setSaleN] = useState(eventData.sale_n);
    const [reSaleN, setReSaleN] = useState(eventData.resale_n);

    const formattedDate = new Date(start.dateTime).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });

    const genre = primaryClassification?.genre?.name || 'Rock';

    const priceDisplay = (priceRanges ?? [false])[0]
        ? `${priceRanges[0].currency} ${priceRanges[0].min} - ${priceRanges[0].max}`
        : 'Price TBA';

    const getBestImage = (images) => {
        let width = 0;
        let selimage = null;
        images.forEach((image) => {
            if(image.width > width) {
                width = image.width;
                selimage = image;
            }
        })
        return selimage.url;
    }

    const parseSale = (sale) => {
        const name = sale.name ?? 'Public';
        const date = sale.startDateTime ? new Date(sale.startDateTime) : 'Now';
        const start = date instanceof Date ? date.toLocaleString('en-UK') : date;
        const started = date instanceof Date ? (date < (new Date())) : true;

        return {name, start, date, started}
    }

    const saleValues = [
        parseSale(sales['public']),
        ...(sales['presales'] ? sales['presales'].map((sale) => parseSale(sale)) : [])
    ];

    const toggleSaleNotification = (type) => {
        if(type === 'sale') {
            setSaleN(!saleN);
            updateEventNotification(event_id, {"sale": !saleN});
        }
        
        if(type === 'resale') {
            setReSaleN(!reSaleN);
            updateEventNotification(event_id, {"resale": !reSaleN});
        }
    }

    return (
        <a href={url} target='_blank' rel='noreferrer' style={{all: 'unset'}}>
        <Container className='my-2'>
        <Card className='event' sx={{ maxWidth: 600, margin: 'auto' }}>
            <CardMedia
            href={url}
            target='_blank'
            component="img"
            height="240"
            image={getBestImage(images)}
            alt={name}
            />
            <CardContent>
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <div className='d-flex'>
                        <Typography variant="h5" component="div">
                            {name}
                        </Typography>
                        <Chip label={genre} className='gg-cream' variant="contained" sx={{ mx: 1 }} />
                    </div>
                </Grid>
                <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                        Your artists:
                    </Typography>
                    <Typography variant="body1">{artists}</Typography>
                </Grid>
                <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                        Date:
                    </Typography>
                    <Typography variant="body1">{formattedDate}</Typography>
                </Grid>
                <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                        Venue:
                    </Typography>
                    <Typography variant="body1">{venue.name}, {country}</Typography>
                </Grid>
                <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                        Price:
                    </Typography>
                    <Typography variant="body1">{priceDisplay}</Typography>
                </Grid>
                <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                        ID:
                    </Typography>
                    <Typography variant="body1">{event_id}</Typography>
                </Grid>
                <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                        Notifications:
                    </Typography>
                    <Button variant={saleN ? 'contained' : 'outlined'} className={'btn m-2 px-3' + (saleN ? ' gg-cream': ' gg-cream-o')}  style={{}}
                        data-mdb-toggle="button"
                        onClick={(e) => {e.stopPropagation(); e.preventDefault(); toggleSaleNotification('sale')}}>
                        General Sale Tickets <Chip className='mx-2' style={{backgroundColor: 'white'}} variant="outlined" label={saleN ? 'ON' : 'OFF'}></Chip>
                    </Button>
                    <Button variant={reSaleN ? 'contained' : 'outlined'} className={'btn m-2 px-3' + (reSaleN ? ' gg-cream': ' gg-cream-o')} style={{}}
                        data-mdb-toggle="button"
                        onClick={(e) => {e.stopPropagation(); e.preventDefault(); toggleSaleNotification('resale')}}>
                        Resale Tickets <Chip className='mx-2' style={{backgroundColor: 'white'}} variant="outlined" label={reSaleN ? 'ON' : 'OFF'}></Chip>
                    </Button>
                </Grid>
                <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                        Sale Times:
                    </Typography>
                    {saleValues.map((sale, idx) => 
                        <Box key={idx} sx={{
                            display: 'flex',
                            alignItems: 'center',
                            border: '1px solid',
                            borderColor: 'divider',
                            borderRadius: 1,
                            padding: 1,
                            marginTop: 1,
                            width: 'fit-content',
                            color: 'text.secondary',
                            '& svg': {
                              m: 1,
                            },
                            '& hr': {
                                mx: 0.5,
                                borderColor: 'text.secondary',
                                my: 0,
                              },
                          }} >
                            <Typography variant="body2">{sale.name}</Typography>
                            <Divider orientation="vertical" variant="middle" flexItem />
                            <Typography variant="body2">{sale.start}</Typography>
                            {sale.started ? <Chip className='mx-1 gg-cream' label='Started'/> : <Chip className='mx-1' color="secondary" label='Soon'/>}
                        </Box>
                    )}
                </Grid>
            </Grid>
            </CardContent>
        </Card>
        </Container>
        </a>
    );
    };

export default Event;
