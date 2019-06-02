import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import { Icon, Table, Rating, Checkbox } from 'semantic-ui-react';
import Moment from 'react-moment';
import { connect } from 'react-redux';
import { fetchUsers, pauseUpdate, userInfoOpen } from '../actions/usersAction';
import { makeSearchParams } from '../utils/urlParams';
import UserInfo from './user-info';

class PeoplePage extends Component {
    componentWillMount() {
        console.log('componentWillMount. Props', this.props);
        this.props.fetchUsers();
    }

    render() {
        const rows = this.props.users.map(user => (
            <Table.Row key={user.id}>
                <Table.Cell>
                    <UserInfo />
                    <Icon name="user" onClick={() => this.props.userInfoOpen(user.id)} />
                    <NavLink
                        to={{
                            pathname: '/photos',
                            search: `${makeSearchParams({ owner_id: user.id, page: 1 }, this.props.location.search)}`
                        }}
                    >
                        <Icon name="rss" />
                    </NavLink>

                    <NavLink
                        to={{
                            pathname: '/photos',
                            search: `${makeSearchParams({ photos_by: user.id, page: 1 }, this.props.location.search)}`
                        }}
                    >
                        <Icon name="copyright" />
                    </NavLink>

                    <NavLink
                        to={{
                            pathname: '/photos',
                            search: `${makeSearchParams({ photos_of: user.id, page: 1 }, this.props.location.search)}`
                        }}
                    >
                        <Icon name="images" />
                    </NavLink>
                </Table.Cell>

                <Table.Cell>{`${user.first_name} ${user.last_name}`}</Table.Cell>

                <Table.Cell>
                    <Rating icon="star" defaultRating={0} maxRating={10} />
                </Table.Cell>
                <Table.Cell>
                    <Moment unix fromNow>
                        {user.date_photos_updated_successfully}
                    </Moment>
                </Table.Cell>
                <Table.Cell>
                    <Checkbox
                        toggle
                        checked={user.pause_update}
                        onChange={() => {
                            this.props.pauseUpdate(user.id, !user.pause_update);
                        }}
                    />
                </Table.Cell>
            </Table.Row>
        ));
        return (
            <div>
                <Table compact celled>
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell />
                            <Table.HeaderCell>Name</Table.HeaderCell>
                            <Table.HeaderCell>Rating</Table.HeaderCell>
                            <Table.HeaderCell>Photos updated</Table.HeaderCell>
                            <Table.HeaderCell>Pause update</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>{rows}</Table.Body>
                </Table>
            </div>
        );
    }
}

function mapStateToProps(state) {
    return { users: state.userReducer.users };
}

export default connect(
    mapStateToProps,
    { fetchUsers, pauseUpdate, userInfoOpen }
)(PeoplePage);
