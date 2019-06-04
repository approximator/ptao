import React, { Component } from 'react';
import { Button, Menu, Pagination, Segment, Form, Sidebar } from 'semantic-ui-react';
import Gallery from 'react-photo-gallery';
import Lightbox from 'react-image-lightbox';
import KeyboardEventHandler from 'react-keyboard-event-handler';
import UserInfo from '../people/user-info';
import TagPeopleDialog from './tag-people';
import Image from './image';
import { makeSearchParams } from '../utils/urlParams';
import { connect } from 'react-redux';
import {
    fetchPhotos,
    lightboxClose,
    lightboxPrev,
    lightboxNext,
    imageClick,
    deletePhotos
} from '../actions/photosActions';
import { tagPeopleDialogOpen } from '../actions/usersAction';
import { shiftUp, shiftDown } from '../actions/keyboardActions';
import 'react-image-lightbox/style.css';

class PhotosPage extends Component {
    constructor(props) {
        super(props);

        this.onPaginationChange = this.onPaginationChange.bind(this);
    }

    componentWillMount() {
        this.props.fetchPhotos(this.props.location.search);
    }

    componentWillReceiveProps(newProps) {
        if (newProps.location.search !== this.props.location.search) {
            this.props.fetchPhotos(newProps.location.search);
        }
    }

    onPaginationChange(e, { activePage }) {
        this.props.history.push(`?${makeSearchParams({ page: activePage }, this.props.location.search)}`);
    }

    handleSort = (e, { value }) => {
        let params = new URLSearchParams(this.props.location.search);
        params.set('sort_by', value);
        params.set('page', 1);
        this.props.history.push(`?${params.toString()}`);
    };

    render() {
        let { photos, sortBy, lightboxIsOpen, currentImage } = this.props;
        let photosSrcs = this.props.photos.map(photo => {
            return photo.src;
        });
        return (
            <div>
                {/* <Icon
                    name="sidebar"
                    style={{ position: 'fixed', top: '80px', left: '5px' }}
                    onClick={() => this.setState({ sidebarVisible: !this.props.sidebarVisible })}
                /> */}
                <Sidebar.Pushable as={Segment}>
                    <Sidebar visible={this.props.sidebarVisible} animation="overlay">
                        <Segment color="green">
                            <h3>filter</h3>
                            <Form>
                                <Form.Group>
                                    <Form.Field>
                                        <label>Sort</label>
                                        <Form.Radio
                                            label="Date taken"
                                            value="date-taken"
                                            checked={sortBy === 'date-taken'}
                                            onChange={this.handleSort}
                                        />
                                        <Form.Radio
                                            label="Date downloaded"
                                            value="date-downloaded"
                                            checked={sortBy === 'date-downloaded'}
                                            onChange={this.handleSort}
                                        />
                                        <Form.Radio
                                            label="Rating"
                                            value="rating"
                                            checked={sortBy === 'rating'}
                                            onChange={this.handleSort}
                                        />
                                    </Form.Field>
                                </Form.Group>
                            </Form>
                        </Segment>
                    </Sidebar>
                    <Sidebar.Pusher>
                        <Gallery photos={photos} onClick={this.props.imageClick} ImageComponent={Image} />
                        {lightboxIsOpen && (
                            <Lightbox
                                mainSrc={photosSrcs[currentImage]}
                                nextSrc={photosSrcs[(currentImage + 1) % photos.length]}
                                prevSrc={photosSrcs[(currentImage + photos.length - 1) % photos.length]}
                                imageCaption={photos[currentImage].text}
                                imageTitle={photos[currentImage].onwer_name}
                                onCloseRequest={this.props.lightboxClose}
                                toolbarButtons={[
                                    <Button
                                        icon="trash"
                                        onClick={() => this.props.deletePhotos([photos[currentImage]])}
                                    />
                                ]}
                                onMovePrevRequest={this.props.lightboxPrev}
                                onMoveNextRequest={this.props.lightboxNext}
                            />
                        )}
                    </Sidebar.Pusher>
                </Sidebar.Pushable>
                <Menu className="secondaryTopMenu" fixed="bottom" inverted>
                    <Pagination
                        inverted
                        // showEllipsis={false}
                        // showFirstAndLastNav={false}
                        boundaryRange={4}
                        siblingRange={1}
                        activePage={this.props.currentPage}
                        onPageChange={this.onPaginationChange}
                        totalPages={this.props.totalPages}
                    />

                    <UserInfo modalTrigger={<Button>New User</Button>} />

                    <TagPeopleDialog />
                    <Button
                        compact
                        onClick={() => {
                            this.props.tagPeopleDialogOpen(this.props.photos.filter(photo => photo.selected === true));
                        }}
                    >
                        Tag People
                    </Button>
                </Menu>

                <KeyboardEventHandler
                    handleKeys={['all']}
                    handleEventType={'keyup'}
                    onKeyEvent={(key, e) => {
                        if (key === 'shift') {
                            this.props.shiftUp();
                        }
                    }}
                />
                <KeyboardEventHandler
                    handleKeys={['all']}
                    onKeyEvent={(key, e) => {
                        console.log(key);
                        if (key === 'del') {
                            console.log(`del key. Lightbox opened: ${this.props.lightboxIsOpen}`);
                            if (this.props.lightboxIsOpen) {
                                this.props.deletePhotos([this.props.photos[this.props.currentImage]]);
                            } else {
                                this.props.deletePhotos(this.props.photos.filter(photo => photo.selected === true));
                            }
                        } else if (key === 'shift') {
                            this.props.shiftDown();
                        }
                    }}
                />
            </div>
        );
    }
}

const mapStateToProps = state => {
    return {
        ...state.photos
    };
};

export default connect(
    mapStateToProps,
    {
        fetchPhotos,
        lightboxClose,
        lightboxNext,
        lightboxPrev,
        imageClick,
        shiftUp,
        shiftDown,
        deletePhotos,
        tagPeopleDialogOpen
    }
)(PhotosPage);
