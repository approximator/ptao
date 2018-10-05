import React, { Component } from 'react';
import { Button, Header, Image, Modal, Input, Card } from 'semantic-ui-react'

class UserInfo extends Component {

    state = {
        userName: '',
        userPhoto: '',
        userUrl: '',
        userId: '',
        userStatusStr: '',

        userHostUrl: '',
        userLocalId: '',
        userPhotosUrl: '',

        infoIsLoading: false,
        gotInfo: false
    }

    constructor(props) {
        super(props)
        this.fetchUserInfo = this.fetchUserInfo.bind(this);
        this.addUser = this.addUser.bind(this);
    }

    componentDidMount() {
        console.log(this.props);
    }

    getUserId(url) {
        const lastSlashIndex = url.lastIndexOf('/');
        if (lastSlashIndex > 0) {
            return url.substring(lastSlashIndex + 1, url.length);
        }
        return url;
    }

    fetchUserInfo() {
        this.setState({ infoIsLoading: true });
        fetch('/api/users/' + this.state.userId + '/update')
            .then(res => res.json())
            .then(data => {
                console.log(data);
                this.setState({
                    userName: data['first_name'] + ' ' + data['last_name'],
                    userPhoto: data['photo'],
                    userId: data['id'],
                    userLocalId: data.local_id ? data.local_id : '',
                    userPhotosUrl: data.local_photos_url ? data.local_photos_url : '',
                    userHostUrl: data.host_url ? data.host_url : '',
                    userStatusStr: data.status_str ? data.status_str : '',
                    gotInfo: true,
                    infoIsLoading: false
                });
            })
            .catch(err => {
                console.error(err)
                this.setState({ infoIsLoading: false });
            })
    }

    addUser() {
        const options = {
            method: 'put',
            headers: { 'Content-type': 'application/json; charset=UTF-8' }
        }
        fetch('/api/users/' + this.state.userId + '/update', options)
            .then(res => res.json())
            .then(data => {
                console.log(data);
            })
            .catch(err => {
                console.error(err)
                this.setState({ infoIsLoading: false });
            })
    }

    render() {
        return (
            <Modal trigger={this.props.modalTrigger} active={true}>
                <Modal.Header>
                    <Input fluid loading={this.state.infoIsLoading}
                        action={{ icon: 'search', onClick: this.fetchUserInfo }}
                        onChange={e =>
                            this.setState({ userUrl: e.target.value, userId: this.getUserId(e.target.value) })
                        }
                        placeholder='Enter url' />
                </Modal.Header>
                <Modal.Content image>
                    <Image wrapped size='medium' src={this.state.userPhoto} />
                    <Modal.Description>
                        {this.state.gotInfo &&
                            <Card>
                                <Card.Content>
                                    <Card.Header>{this.state.userName}</Card.Header>
                                    <Card.Meta>
                                        <a href={this.state.userHostUrl}>Host URL</a>
                                        {this.state.userPhotosUrl &&
                                            <a href={this.state.userPhotosUrl}>Local photos</a>
                                        }
                                    </Card.Meta>
                                    <Card.Description>
                                        {this.state.userStatusStr}
                                    </Card.Description>
                                </Card.Content>
                                <Card.Content extra>

                                    <div className='ui two buttons'>
                                        <Button basic color='green' onClick={this.addUser}>
                                            Add
                                        </Button>
                                        <Button basic color='red'>
                                            Calcel
                                        </Button>
                                    </div>
                                </Card.Content>
                            </Card>
                        }
                    </Modal.Description>
                </Modal.Content>
            </Modal>
        );
    }
}

export default UserInfo;
