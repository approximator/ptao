import React, { Component } from 'react';
import { Button, Label, Icon, Menu, Pagination } from 'semantic-ui-react'
import Gallery from 'react-grid-gallery';
import KeyboardEventHandler from 'react-keyboard-event-handler';
import UserInfo from '../people/user-info';
import TagPeopleDialog from './tag-people';

class PhotosPage extends Component {

    state = {
        photos: [],
        currentImage: 0,
        lightboxOpened: false,
        totalPhotosCount: undefined,
        totalPages: undefined,
        currentPage: 1,
        photosPerPage: 200,
        shiftPressed: false,

        tagPeopleModalOpened: false,
        selectedImages: []
    }

    constructor(props) {
        super(props)

        this.onPaginationChange = this.onPaginationChange.bind(this);
        this.onCurrentImageChange = this.onCurrentImageChange.bind(this);
        this.onSelectImage = this.onSelectImage.bind(this);
    }

    componentWillReceiveProps(newProps) {
        if (newProps.location.search != this.props.location.search) {
            this.fetchPhotos(newProps.location.search);
        }
    }

    componentDidMount() {
        this.fetchPhotos(this.props.location.search)
    }

    fetchPhotos(searchParams) {
        let params = new URLSearchParams(searchParams);
        const page = params.has("page") ? parseInt(params.get('page')) : 1;
        const photosPerPage = params.has("elements_per_page") ? parseInt(params.get('elements_per_page')) : 200;
        params.set('page', page);
        params.set('elements_per_page', photosPerPage);
        const url = '/api/photos?' + params.toString()
        console.log('Requesting: ' + url)
        fetch(url)
            .then(res => res.json())
            .then(data => {
                console.log(data);
                this.setState({
                    photos: data.photos.map(photo => this.createImgObj(params.has("missing"), photo)),
                    totalPhotosCount: data['count'],
                    totalPages: Math.ceil(Number(data['count']) / photosPerPage)
                });
                window.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });
            })
        this.setState({
            currentPage: parseInt(params.get('page')),
            photosPerPage: photosPerPage
        })
    }

    onPaginationChange(e, { activePage }) {
        let params = new URLSearchParams(this.props.location.search);
        params.set('page', activePage)
        this.props.history.push(`?${params.toString()}`);
        console.log(`Current page ${activePage}`)
    }

    onClickSelectAll() {
        let photos = this.state.photos.slice();
        const isAllSelected = photos.filter(photo => photo.isSelected === true).length === photos.length

        photos.forEach(img => { img.isSelected = !isAllSelected; });
        this.setState({
            photos: photos
        });
    }

    onSelectImage(index, image) {
        var photos = this.state.photos.slice();
        var img = photos[index];
        img.isSelected = img.hasOwnProperty("isSelected") ? !img.isSelected : true;

        this.setState({
            photos: photos
        });
    }

    onCurrentImageChange(index) {
        this.setState({ currentImage: index });
    }

    getSelectedImages() {
        return this.state.photos.filter(photo => photo.isSelected === true);
    }

    createImgObj(is_missing, photo) {
        return {
            id: photo.id,
            owner_id: photo.owner_id,
            onwer_name: photo.owner.first_name + ' ' + photo.owner.last_name,
            src: is_missing ? photo.url : photo.local_url,
            thumbnail: is_missing ? photo.url : photo.local_url,
            text: photo.text,
            caption: photo.text,
            thumbnailWidth: photo.width,
            thumbnailHeight: photo.height,
            tags: photo.people.map(user => {
                return { value: user.first_name + ' ' + user.last_name, title: user.first_name + ' ' + user.last_name }
            })
        }
    }

    removeImages(imgs) {
        console.log(imgs)
        const data = {
            photos: imgs.map(img => img.id)
        }

        const options = {
            method: 'delete',
            headers: { 'Content-type': 'application/json; charset=UTF-8' },
            body: JSON.stringify(data)
        }

        fetch('/api/photos', options)
            .then(response => response.json())
            .then(body => {
                console.log(body)
                this.setState({ photos: this.state.photos.filter(photo => !imgs.includes(photo)) });
            })
            .catch(err => console.error(err))
    }

    removeSelectedImages() {
        let selectedImgs = this.getSelectedImages()
        this.removeImages(selectedImgs)
    }

    goToAuthor(owner_id) {
        let params = new URLSearchParams(this.props.location.search);
        params.set('owner_id', owner_id);
        params.set('page', 1);
        this.props.history.push(`?${params.toString()}`);
    }

    linksFromDescription(description) {
        if (description === undefined) {
            return;
        }

        const matches = description.match(/\[(id\d+)(.*?)\]/gmi);
        if (!matches) {
            return;
        }
        const links  = matches.map(match => match.substring(1, match.length-1).split('|'));
        return links.map(link =>
            <a href={`https://vk.com/${link[0]}`} style={linkStyle} >{link[1]}</a>
        )
    }

    render() {
        var photos = this.state.photos.map(photo => {
            photo.customOverlay = (
                <div style={captionStyle}>
                    <Label as='a' style={{ pointerEvents: "auto" }} onClick={() => { this.goToAuthor(photo.owner_id); }}>
                        <Icon name='copyright outline' /> {photo.onwer_name}
                    </Label>
                    {this.linksFromDescription(photo.text)}
                </div>);
            return photo;
        });

        return (
            <div>
                <Menu className="secondaryTopMenu" fixed='bottom' inverted>
                    <Button compact toggle active={this.state.selectAllChecked} onClick={() => this.onClickSelectAll()}>
                        Select All
                    </Button>

                    <Pagination inverted
                        showEllipsis={false}
                        showFirstAndLastNav={false}
                        boundaryRange={4}
                        siblingRange={1}
                        activePage={this.state.currentPage}
                        onPageChange={this.onPaginationChange}
                        totalPages={this.state.totalPages}
                    />

                    <UserInfo modalTrigger={<Button>New User</Button>} />
                    <TagPeopleDialog
                        modalOpen={this.state.tagPeopleModalOpened}
                        photos={this.state.selectedImages}
                    />
                    <Button compact onClick={() => {
                        const selectedImgs = this.getSelectedImages().slice();
                        this.setState({
                            tagPeopleModalOpened: true,
                            selectedImages: selectedImgs
                        })
                        console.log(`selected images: ${selectedImgs}`)
                    }}>
                        Tag People
                    </Button>
                </Menu>

                <Gallery
                    images={photos}
                    rowHeight={250}
                    onSelectImage={this.onSelectImage}
                    currentImageWillChange={this.onCurrentImageChange}
                    lightboxWillOpen={() => this.setState({ lightboxOpened: true })}
                    lightboxWillClose={() => this.setState({ lightboxOpened: false })}

                    customControls={[
                    ]}
                />

                <KeyboardEventHandler
                    handleKeys={['del', 'shift']}
                    onKeyEvent={(key, e) => {
                        if (key === "del") {
                            console.log(`del key. Lightbox opened: ${this.state.lightboxOpened}`)
                            if (this.state.lightboxOpened) {
                                this.removeImages([this.state.photos[this.state.currentImage]]);
                            } else {
                                this.removeSelectedImages();
                            }
                        }
                    }}
                >
                </KeyboardEventHandler>
            </div>
        );
    }
}

const captionStyle = {
    backgroundColor: "rgba(0, 0, 0, 0.2)",
    overflow: "hidden",
    position: "absolute",
    bottom: "0",
    width: "100%",
    color: "white",
    padding: "2px"
};

const linkStyle = {
    pointerEvents: "auto",
    wordWrap: "break-word",
    display: "inline-block",
    backgroundColor: "rgba(.5, .5, 0, 0.2)",
    height: "auto",
    fontSize: "75%",
    fontWeight: "600",
    lineHeight: "1",
    padding: ".2em .6em .3em",
    borderRadius: ".25em",
    color: "blue",
    verticalAlign: "baseline",
    margin: "2px"
};

export default PhotosPage;
