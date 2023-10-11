import streamlit as st
from streamlit_elements import elements, dashboard, mui, editor, media, lazy, sync, nivo


class Portfolio:
	def __init__(self, cards=None):
		self.max_weight = 100.
		self.cards = None
		if cards is not None:
			self.populate(cards)

	def populate(self, cards):
		self.max_weight = max(10., min(float(int(420 / len(cards))//10*10), 100.))
		for c in cards:
			c.weight = 100/len(cards)
			c.max_weight = self.max_weight
			c.set_portfolio(self)
		self.cards = cards

	def update_weight(self, card, new_value):
		other = [c for c in self.cards if c != card and not c.locked]
		delta = card.weight - new_value
		fixed = sum(c.weight for c in self.cards if c.locked)
		current = sum(c.weight for c in other)

		if not len(other):
			st.error(f'Cannot update weight of {card.name} because it is the only unlocked card.')

		for c in other:
			new = c.weight + delta * (1/len(other) if current == 0 else c.weight / current)
			c.weight = min(max(0., new), 100.)

		card.weight = 100 - (fixed + sum(c.weight for c in other))

	def display(self):
		with st.sidebar:
			with st.expander('Sort'):
				st.button('by weight')

				st.multiselect('Group Sector', ['Tech', 'Healthcare', 'Energy', 'Financials', 'Consumer Staples'])
				st.multiselect('Group Country', ['Germany', 'France', 'Netherlands'])

				st.selectbox('by Stat', ['', 'Market Cap', 'Beta', 'Risk'])

			with st.expander('Filter'):
				st.button('Unselect all')
				st.multiselect('Select sectors', ['Tech', 'Healthcare', 'Energy', 'Financials', 'Consumer Staples'])

				d_col, q_col = st.columns([1, 5])
				with d_col:
					st.button('↗️' if True else '↘️', help='Show only stocks with higher/lower weight')
				with q_col:
					st.number_input('Weight', 0., 100., None, label_visibility='collapsed')

				col1, col2, col3 = st.columns(3)
				with col1:
					st.button('Focus', help='Hide all but selected')
				with col2:
					st.button('Hide', help='Hide selected')
				with col3:
					st.button('Reset', help='Show all')

			hidden = [c for c in self.cards if c.hidden]
			st.write(f'Showing {len(self.cards) - len(hidden)} of {len(self.cards)} stocks.')
			# if len(hidden):
			# 	st.button('Clear Filter')

			st.title('Stocks')
			for card in self.cards:
				if not card.hidden:
					card.display()


class Card:
	def __init__(self, name: str, weight=1., max_weight=100., portfolio=None):
		self.p = portfolio
		self.name = name
		self.weight = weight
		self.max_weight = max_weight
		self.locked = False
		self.selected = False
		self.hidden = False

	def set_portfolio(self, portfolio):
		self.p = portfolio

	def toggle_lock(self):
		self.locked = not self.locked

	def toggle_select(self):
		self.selected = not self.selected
		st.write(f'{self.name} is selected: {self.selected}')

	def update_weight(self):
		self.p.update_weight(self, float(st.session_state[f'weight_{self.name}']))
		return self.weight

	def display(self):
		# with st.expander(self.name):
		# 	st.write('Company profile and details') # TODO: company details

		with st.container():
			# st.subheader(f'{self.name}')

			s_col, t_col = st.columns([1, 10])
			with s_col:
				st.checkbox('Select', key=f'select_{self.name}', on_change=self.toggle_select, label_visibility='collapsed')
			with t_col:
				with st.expander(self.name):
					st.write('Company profile and details')

			# st.checkbox(f'{self.name}')

			w_col, l_col = st.columns([5, 1])
			with w_col:
				st.slider('Weight', 0., self.max_weight,
										self.weight,
										key=f'weight_{self.name}',
										disabled=self.locked, on_change=self.update_weight, label_visibility='collapsed')
				# st.markdown(f'<p style="color:#333;">{self.name}</p>', unsafe_allow_html=True)
			with l_col:
				st.button('🔓' if self.locked else '🔒', key=f'lock_{self.name}', on_click=self.toggle_lock)












