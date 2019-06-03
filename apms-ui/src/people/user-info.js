import React, { Component } from 'react';
import { Button, Image, Modal, Input, Card, Dropdown } from 'semantic-ui-react';
import { connect } from 'react-redux';
import { userInfoClose, updateUserInfoDefaultPersons } from '../actions/usersAction';

class UserInfo extends Component {
    getUserId(url) {
        const lastSlashIndex = url.lastIndexOf('/');
        if (lastSlashIndex > 0) {
            return url.substring(lastSlashIndex + 1, url.length);
        }
        return url;
    }

    render() {
        let user = this.props.currentUser;
        return (
            user !== undefined && (
                <Modal size="large" open={this.props.isOpen} onClose={this.props.userInfoClose}>
                    <Modal.Header>
                        <Input
                            fluid
                            loading={true}
                            action={{ icon: 'search', onClick: () => this.props.fetchUserInfo(this.state.userId) }}
                            onChange={e =>
                                this.setState({ userUrl: e.target.value, userId: this.getUserId(e.target.value) })
                            }
                            placeholder="Enter url"
                        />
                    </Modal.Header>
                    <Modal.Content image>
                        <Image wrapped size="medium" src={user.photo} />
                        <Modal.Description>
                            <Card>
                                <Card.Content>
                                    <Card.Header>{`${user.first_name} ${user.last_name}`}</Card.Header>
                                    <Card.Meta>
                                        <a href={user.url}>Host URL</a>
                                    </Card.Meta>
                                    <Card.Description>{user.status_str}</Card.Description>
                                </Card.Content>
                            </Card>

                            <Card>
                                <Card.Content>
                                    <h5>Default autor:</h5>
                                    <Dropdown
                                        search
                                        selection
                                        placeholder="Choose someone"
                                        options={this.props.peopleDropdownList}
                                        defaultValue={user.default_author}
                                        onChange={(e, { value }) => {
                                            this.setState({ default_author: value });
                                        }}
                                    />

                                    <h5>Default person to tag:</h5>
                                    <Dropdown
                                        search
                                        selection
                                        placeholder="Choose someone"
                                        options={this.props.peopleDropdownList}
                                        defaultValue={user.default_person_to_tag}
                                        onChange={(e, { value }) => {
                                            this.setState({ default_person_to_tag: value });
                                        }}
                                    />
                                </Card.Content>
                                <Card.Content extra>
                                    <div className="ui two buttons">
                                        <Button
                                            basic
                                            color="green"
                                            onClick={() => {
                                                this.props.updateUserInfoDefaultPersons(
                                                    user.id,
                                                    this.state ? this.state.default_author : undefined,
                                                    this.state ? this.state.default_person_to_tag : undefined
                                                );
                                            }}
                                        >
                                            Update
                                        </Button>
                                        <Button basic color="red">
                                            Cancel
                                        </Button>
                                    </div>
                                </Card.Content>
                            </Card>
                        </Modal.Description>
                    </Modal.Content>
                </Modal>
            )
        );
    }
}

function mapStateToProps(state) {
    return {
        currentUser: state.userReducer.users.find(usr => usr.id === state.userReducer.currentUser),
        isOpen: state.userReducer.userInfoOpen,
        peopleDropdownList: state.userReducer.peopleDropdownList
    };
}

export default connect(
    mapStateToProps,
    { userInfoClose, updateUserInfoDefaultPersons }
)(UserInfo);
